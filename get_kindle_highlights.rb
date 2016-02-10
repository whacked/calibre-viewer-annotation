###
# script to download all available notes from amazon kindle into
# yml files for further processing.
# USAGE:
# ruby get_kindle_highlights.rb [output-directory-path]

require 'yaml'
require 'io/console'
require 'kindle_highlights'
require 'nokogiri'

def setup
  # for development convenience this will credentials from ~/.aws/kindle
  # THIS IS NOT RECOMMENDED!
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
  kindle_config_filepath = File.join(Dir.home, '.aws', 'kindle')
  if File.exists? kindle_config_filepath then
    puts 'loading from config file...'
    conf = JSON.parse File.read kindle_config_filepath
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

def make_output_filename(book_name)
  return "#{book_name}.yml"
end

def save(basedir, k, id)
  puts k.books[id]
  d = {
    'title' => k.books[id],
    'highlight_list' => k.highlights_for(id),
  }
  ofile = File.join(basedir, make_output_filename(k.books[id]))
  File.open(ofile, 'w') {|f| f.write(d.to_yaml)}
  "ok: #{ofile}"
end

def download_for_asin(kindle, asin)
  # it turns out highlights_for calls some internal Amazon API, which doesn't
  # itself return notes; therefore, we need to call and parse from
  # https://kindle.amazon.com/your_highlights_and_notes/
  # However, your_highlights_and_notes doesn't the timestamp, so we need call
  # both, and combine them.

  # first retrieve the highlight list.
  highlight_list = kindle.highlights_for(asin)
  
  # extract the mechanize client out of the kindle client
  mech = kindle.instance_variable_get(:@mechanize_agent)
  endpoint = "https://kindle.amazon.com/your_highlights_and_notes/#{asin}"

  highlights_and_notes_page = mech.get(endpoint)
  # realistically, we expect each endLocation to appear only once,
  # because why would you create 2 highlights to the same passage
  # ending, but you never know, so we'll make a
  # Hash[endLocation => highlight]
  endLocation_mapping = highlight_list.inject({}) do |out, highlight_entry|
    endLocation = highlight_entry['endLocation']
    if not out.include? endLocation then
      out[endLocation] = []
    end
    out[endLocation].push(highlight_entry)
    out
  end

  npage = Nokogiri::HTML(highlights_and_notes_page.body)
  npage.css('.highlightRow.yourHighlight').each do |html_entry|
    # need to match the endLocation => highlight mapping to be a hit
    highlight = html_entry.css('.highlight').text
    endLocation = html_entry.css('.hidden.end_location').text.to_i

    if not endLocation_mapping.include? endLocation then
      puts('WARNING! MISMATCH OF endLocation FOUND!!!')
      puts("searched for #{endLocation}")
      puts("among: #{endLocation_mapping.keys}")
      next
    end

    note_text = html_entry.css('.noteContent').text
    if note_text.length == 0 then
      next
    end

    endLocation_mapping[endLocation].each do |highlight_entry|
      if highlight_entry['highlight'] == highlight then
        # exact match!!!
        # puts("modifying entry with note!")
        highlight_entry['note'] = note_text
        break
      end
    end
  end

  highlight_list
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
    if File.exists? candidate_output
      puts "*** already saved:\n    #{k.books[bkid]}"
      puts "delete \"#{candidate_output}\" if you want to re-download it."
      next
    end
    puts "saving #{bkid}"
    save(output_dir, k, bkid)
  end
end
