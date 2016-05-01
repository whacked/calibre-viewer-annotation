__doc__ = <<-EOS
proof of concept / utility script

the import process:

  ruby #{$0} PATH_TO_YML_FILE


1.  using input argument, load the highlights file exported from get_kindle_highlights or whatever tool
2.  query `calibredb` and find out where the local book is stored
3.  launch the `nw-extractor` app with requisite parameters.
4.  (manual) reconcile the matches in `nw-extractor` and generate importable json file
5.  output the command to import the json file
6.  run the command, check the output
7.  run the command again with DRY_RUN=FALSE

EOS

if ARGV.length < 1
  puts __doc__
  exit
end

require 'yaml'
require 'json'
require 'kindle_highlights'
require 'io/console'

begin
  require 'fuzzystringmatch'
  puts 'fuzzy title matching enabled'
  $matcher = FuzzyStringMatch::JaroWinkler.create( :pure )
  def is_match(s1, s2)
    $matcher.getDistance(s1, s2) > 0.9
  end
rescue
  puts 'fuzzy string matching not available. will attempt exact title matches'
  puts 'to enable fuzzy matching, run "gem install fuzzy-string-match"'
  def is_match(s1, s2)
    s1 == s2
  end
end

CWD = Dir.getwd
yml_path = File.absolute_path(ARGV[0])
note_data = YAML.load File.open(yml_path)
CALIBRE_LIBRARY_PATH = File.join(ENV['HOME'], 'Calibre Library')

# here we find the book id, to locate the local file
epub_id = nil
# a small -w (wrap) will cause linebreaks in the title
`calibredb list -f title -w 9999`.lines.each do |line|
  id, title = line.strip.split(/\s+/, 2)
  next unless id =~ /\d+/ # really just the first line, which outputs 'id  title', the column heads

  if is_match(title, note_data['title'])
    puts "found match #{title}"
    puts "    vs      #{note_data['title']}"
    epub_id = id.to_i
    break
  end
end

if not epub_id.nil?
  epub_path = Dir.glob(File.join(CALIBRE_LIBRARY_PATH, '*', "*(#{epub_id})", "*.epub"))[0]

  puts "======================"
  puts "USING:"
  puts yml_path
  puts epub_path
  puts "======================"

  # NOTE: will no longer work:
  # Dir.chdir('nw-extractor')
  # `nw . '#{epub_path}' '#{yml_path}'`
  # json_path = yml_path.sub(".yml", ".json")
  # Dir.chdir(CWD)
  puts "use the match-tool and generate the output json."

  puts "THEN RUN THIS:"
  puts " python importjson.py 'json_path' '#{epub_path}'"
end

