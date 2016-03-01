###
# script to download all available notes from amazon kindle into
# yml files for further processing.
# USAGE:
# ruby get_kindle_highlights.rb [output-directory-path]

begin
  require 'gpgme'
  USE_GPG = true
rescue LoadError => e
  USE_GPG = false
  puts <<-EOS
  #{e.message}
  
  could not require 'gpgme' gem. loading of gpg files will not work.

  you can try running 'gem install gpgme' to get this to work.
EOS
end

require 'yaml'
require 'io/console'
require 'kindle_highlights'
require 'nokogiri'

def setup
  # for convenience this will first look for credentials from
  # ~/.aws/kindle.gpg <-- preferred
  # ~/.aws/kindle     <-- not preferred
  #
  # in addition, the kindle config file can contain an 'ignore' key, which
  # should map to an array of strings to match against.  After the
  # (Hash)`books` is populated, each key => value in the Hash will get matched
  # against the entries within the 'ignore' array; if key OR value matches the
  # ignore entry, the key => value is removed from the (Hash)`books`.
  #
  # the entries in 'ignore' are treated as regex if they start and end with
  # a slash; i.e. in
  # ["Some title", "B000ASIN123", "/.000ASIN0.+/"]
  # we will have 2 exact tests and 1 regex test
  kindle_config_filepath = File.join(Dir.home, '.aws', 'kindle' + (USE_GPG ? '.gpg' : ''))
  if File.exists? kindle_config_filepath then
    puts 'loading from config file...'

    if USE_GPG then
      crypto = GPGME::Crypto.new
      decrypted = crypto.decrypt File.open(kindle_config_filepath)
      conf = JSON.parse decrypted.to_s
    else
      conf = JSON.parse File.read kindle_config_filepath
    end
    email = conf['email']
    passw = conf['password']
    ignore = conf['ignore'] or []
  else
    puts 'amazon account email: '
    email = gets.chomp
    puts 'amazon account password:'
    passw = STDIN.noecho(&:gets).chomp
    ignore = []
  end

  kindle = KindleHighlights::Client.new(email, passw)
  
  # process ignore
  kindle.books.each {|asin, title|
    for matcher in ignore do
      is_found = false
      for test_string in [asin, title] do
        if matcher.length > 2 and matcher[0] == '/' and matcher[0] == matcher[-1] then
          is_found = Regexp.new(matcher[1...-1]).match(test_string)
        else
          is_found = matcher == test_string
        end
        if is_found then
          break
        end
      end

      if is_found then
        kindle.books.delete asin
      end
    end
  }

  return kindle
end


# caching
if not defined? $cached_mech_get       then $cached_mech_get = {} end
if not defined? $cached_highlights_for then $cached_highlights_for  = {} end


def load_page(kindle, endpoint)
  result = $cached_mech_get[endpoint]
  if result.nil?
    puts "loading endpoint: #{endpoint}"
    mech = kindle.instance_variable_get(:@mechanize_agent)
    result = $cached_mech_get[endpoint] = mech.get(endpoint)
  else
    puts "reading from cache: #{endpoint}"
  end
  result
end

def parse_highlights_page(page)
  # assumes each endLocation can only have at most 1 highlight and 1 note
  # attached to it.
  # `out` is the return structure
  if page.is_a? Nokogiri::HTML::Document
    ndoc = page
  elsif page.is_a? String
    ndoc = Nokogiri::HTML page
  elsif page.is_a? Mechanize::Page
    ndoc = Nokogiri::HTML page.body
  end
  top_match = ndoc.css('.bookMain.yourHighlightsHeader')[0]

  out = {
    title: top_match.css('.title').text,
    asin: top_match.css('.title a').attr('href').value.split('/')[-1],
    lastHighlighted: Date.parse(top_match.css('.lastHighlighted').text),
    highlightMapping: {}, # endLocation => highlight text
    noteMapping: {}, # endLocation => note text
  }
  top_match.css('.yourHighlightsStats').css('.boldText').each do |stat_item|
    # boldText highlightCountXYZXYZ
    # boldText noteCountXYZXYZ
    kname = stat_item.attr('class').sub(/.* (.+Count).+/, '\1').to_sym
    out[kname] = stat_item.text
  end

  ndoc.css('.highlightRow.yourHighlight').each do |entry|
    # need to match the endLocation => highlight mapping to be a hit
    highlight = entry.css('.highlight').text
    endLocation = entry.css('.hidden.end_location').text.to_i

    note_text = entry.css('.noteContent').text
    if note_text.length > 0 then
      out[:noteMapping][endLocation] = note_text
    end

    out[:highlightMapping][endLocation] = highlight
  end
  return out
end

def get_combined_annotation_list(kindle, asin)
  # it turns out highlights_for calls some internal Amazon API, which doesn't
  # itself return notes; therefore, we need to call and parse from
  # https://kindle.amazon.com/your_highlights_and_notes/
  # However, your_highlights_and_notes doesn't the timestamp, so we need call
  # both, and combine them.

  # first retrieve the highlight list.
  if not $cached_highlights_for.has_key? asin
    puts "loading highlights for #{asin}"
    $cached_highlights_for[asin] = kindle.highlights_for(asin)
  end
  highlight_list = Marshal.load(Marshal.dump($cached_highlights_for[asin]))
  
  # extract the mechanize client out of the kindle client
  mech = kindle.instance_variable_get(:@mechanize_agent)
  endpoint = "https://kindle.amazon.com/your_highlights_and_notes/#{asin}"
  highlights_and_notes_page = load_page(kindle, endpoint)
  allNoteData = parse_highlights_page(highlights_and_notes_page)

  # probably will never run, but just in case
  dupecheck = Hash.new(0)
  highlight_list.map{|entry| dupecheck[entry['endLocation']] += 1}
  dupecheck.each do |endLocation, count|
    if count > 1
      puts("WARNING! #{endLocation} appears more than once!")
    end
  end

  note_data = allNoteData[:noteMapping].clone
  #
  # it turns out some entries have endLocations that are off by 1. wtf?
  # so we will loop over different offset values until everything is
  # matched or we give up
  [0, 1, -1, 2, -2].each do |try_offset|
    if try_offset != 0
      puts "... retrying with offset #{try_offset}"
    end
    highlight_list.each do |entry|
      endLocation = entry['endLocation'] + try_offset
      note_text = note_data[endLocation]
      if not note_text.nil?
        if entry.include? 'note' then
          puts "CONFLICT!"
          puts "    #{note_text}"
          puts " at #{endLocation}"
        else
          entry['note'] = note_text
        end
      end
      note_data.delete endLocation
    end

    if note_data.empty?
      puts "everything checks out!"
      break
    else
      puts "#{note_data.length} notes remaining to match."
    end
  end

  note_data.each do |endLocation, note|
    puts "NOT MATCHED:"
    puts "    #{note}"
    puts " at #{endLocation}"
  end

  return highlight_list
end

def get_most_recent_book(kindle)
  endpoint = "https://kindle.amazon.com/your_highlights"
  # most recent will appear as first result. if you scroll down, more will
  # load. but we only want page 1
  most_recent_highlights_page = load_page(kindle, endpoint)
  parse_highlights_page(most_recent_highlights_page)
end

def make_output_filename(book_name)
  "#{book_name}.yml"
end

def save(basedir, k, asin)
  puts k.books[asin]
  ofile = File.join(basedir, make_output_filename(k.books[asin]))
  File.open(ofile, 'w') {|f| f.write({
    'title' => k.books[asin],
    'highlight_list' => get_combined_annotation_list(k, asin),
  }.to_yaml)}
  "ok: #{ofile}"
end

if __FILE__ == $0
  # if in irb,
  # load 'get_kindle_highlights.rb'
  
  output_dir = ARGV[0] || 'kindle-highlights'
  if not File.exists? output_dir then
    puts "creating output directory: #{output_dir}"
    Dir.mkdir output_dir
  end
  k = setup
  k.books.keys.each do |bkid|
    candidate_output = File.join(output_dir, make_output_filename(k.books[bkid]))

    ## now,
    # kindle.books
    # > { "B00EXAMPLE" => "Some Book Title", ... }
    ## to get highlights, pass the ASIN
    # kindle.highlights_for("B00EXAMPLE")
    # > [{"asin" => "B00EXAMPLE", "customerId" ... "highlight": "Some highlighted text", ... } ... ]
    ## refer to https://github.com/speric/kindle-highlights
  
    if File.exists? candidate_output
      puts "*** already saved:\n    #{k.books[bkid]}"
      puts "delete \"#{candidate_output}\" if you want to re-download it."
      next
    end
    puts "saving #{bkid}"
    save(output_dir, k, bkid)
  end
end
