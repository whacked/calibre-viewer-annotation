<?python from turbogears.i18n import format_date ?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to TurboGears</title>
</head>
<body>
  
  <h2>Movie Store</h2>
  
  <h3>Movies in stock:</h3>
  <table>
    <thead>
      <th>Title</th>
      <th>Director</th>
      <th>Release Date</th>
      <th>*</th>
    </thead>
    <tr py:for="movie in movies">
      <td py:content="movie.title" />
      <td py:content="movie.director.name" />
      <td py:content="format_date(movie.releasedate)" />
      <td>
        <a href="${tg.url('/movie/%d' % movie.id)}">details</a>
      </td>
    </tr>
  </table>
  
</body>
</html>