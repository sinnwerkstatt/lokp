<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      i18n:domain="pyramid_i18n_howto">
    <head>
        <title>${_("User Activation Success")}</title>
        <!-- Meta Tags -->
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style type="text/css">
            div.login {
                border: 1px solid silver;
                padding: 10px;
                width: 200px;
                margin: 0 auto;
                margin-bottom: 5px;
                margin-top: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                text-align: center;
            }
            select, input {
                margin-left: 30px;
            }
            .error {
                background-color: #F68E1D;
            }
        </style>
    </head>

    <body>
        <div class="login">
            <a href="/">
                <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" alt="${_(u'Land Observatory')}"/>
            </a><br/>
            ${_(u"User activation")}<br/>
        </div>
        <div class="login" style="text-align: left;">
            <b>${username}</b><br/>
            ${_(u"Account activation was successful. Your account will be approved during the next days.")}
        </div>
    </body>
</html>