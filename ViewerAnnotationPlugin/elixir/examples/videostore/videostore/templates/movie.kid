<?python from turbogears.i18n import format_date ?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to TurboGears</title>
</head>
<body>
  
  <h2 py:content="movie.title" />
  
  <h3>Release Date</h3>
  <span py:content="format_date(movie.releasedate)" />
  
  <h3>Director</h3>
  <a href="${tg.url('/director/%d' % movie.director.id)}" py:content="movie.director.name" />
  
  <h3>Description</h3>
  <p py:content="movie.description" />
  
  <h3>Cast</h3>
  <ul>
    <li py:for="actor in movie.actors">
      <a href="${tg.url('/actor/%d' % actor.id)}"  py:content="actor.name" />
    </li>
  </ul>
  
</body>
</html>