<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
  <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
  
  <title py:replace="''">Video Store</title>
  <meta py:replace="item[:]"/>
  
  <style type="text/css" media="screen">
    @import "/static/css/style.css";
    @import "/static/css/login.css";
  </style>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
  <div py:if="tg.config('identity.on', False) and not 'logging_in' in locals()" id="pageLogin">
    <span py:if="tg.identity.anonymous">
      <a href="/login">Login</a>
    </span>
    <span py:if="not tg.identity.anonymous">
      Welcome ${tg.identity.user.display_name}.
      <a href="/logout">Logout</a>
    </span>
  </div>
  
  <div py:if="value_of('tg_flash', None)" class="flash" py:content="tg_flash"></div>

  <div py:replace="[item.text]+item[:]"/>
</body>

</html>
