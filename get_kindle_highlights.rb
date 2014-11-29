require 'yaml'
require 'kindle_highlights'

def setup
    KindleHighlights::Client.new('email', 'password')
end

def save(k, id)
  puts k.books[id]
  d = {
    'title' => k.books[id],
    'highlight_list' => k.highlights_for(id),
  }
  ofile = "/tmp/#{k.books[id]}.yml"
  File.open(ofile, 'w') {|f| f.write(d.to_yaml)}
  "ok: #{ofile}"
end

## demo usage:
# k = setup
# k.books.keys.each do |bkid| save(k, bkid) end
