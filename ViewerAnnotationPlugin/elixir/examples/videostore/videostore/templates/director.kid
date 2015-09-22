<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to TurboGears</title>
</head>
<body>
  
  <h2 py:content="director.name" />
  
  <h3>Movies</h3>
  <ul>
    <li py:for="movie in director.movies">
      <a href="${tg.url('/movie/%d' % movie.id)}" py:content="movie.title" />
    </li>
  </ul>
  
</body>
</html>