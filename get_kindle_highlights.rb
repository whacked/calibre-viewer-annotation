###
# script to download all available notes from amazon kindle into
# yml files for further processing.
# USAGE:
# ruby get_kindle_highlights.rb [output-directory-path]

require 'yaml'
require 'io/console'
require 'kindle_highlights'

def setup
  # for development convenience this will credentials from ~/.aws/kindle
  # THIS IS NOT RECOMMENDED!
  cred_filepath = File.join(Dir.home, '.aws', 'kindle')
  if File.exists? cred_filepath then
    puts 'loading from credentials file...'
    cred = JSON.parse File.read cred_filepath
    email = cred['email']
    passw = cred['password']
  else
    puts 'amazon account email: '
    email = gets.chomp
    puts 'amazon account password:'
    passw = STDIN.noecho(&:gets).chomp
  end

  KindleHighlights::Client.new(email, passw)
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
