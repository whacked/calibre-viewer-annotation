###
# script to download all available notes from amazon kindle into
# yml files for further processing.
# USAGE:
# ruby get_kindle_highlights.rb [output-directory-path]

require 'yaml'
require 'io/console'
require 'kindle_highlights'

def setup
  puts 'amazon account email: '
  email = STDIN.gets.strip
  puts 'amazon account password:'
  passwd = STDIN.noecho(&:gets).strip
  KindleHighlights::Client.new(email, passwd)
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
