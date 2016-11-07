title: 关于flask-skeleton
date: 2017-06-10
tags: []

每开始一个Flask项目总是要重复做一些代码结构上的规划和写一些相同的代码，
flask-skeleton的目的是想把这些重复的事情都先统一做成脚手架，
在以后的API服务开发过程中只需clone下来就可以直接开始写业务代码。



## 开发运行

建议使用virtualenv创建虚拟环境。

    virtualenv venv
    source venv/bin activate
    pip install -r requirements.txt
    python apiserver.py

## 文档

运行apiserver后访问：

静态文档：<http://localhost:5000/docs>

API文档： <http://localhost:5000/apidocs>

## 配置

所有配置选项都在`settings.py中`，其中都是配置的默认值，修改这些默认配置的方式不建议直接修改，应使用在`app`目录下新建`.env`的文件的方式进行覆盖，可以参考`app\.env.example`

**装饰器**

在demo的`views.py`中会为`handlers.py`中的函数注册装饰器，这些装饰器不是必须的，
但是在使用时需要注意其注册顺序，按列表顺序注册，先注册的先执行。

使用`register_decorators_on_module_funcs`方法可以自动为一个模块文件中的方法注册装饰器

使用`peewee_mysql context manager`: 确保在使用peewee时都先connect，最后close。如果想查看实际执行的sql可以修改`settings.py`中的`LOG_PEEWEE_SQL=True`

`cached_call`: 根据settings中的配置缓存调用结果，默认不生效，如果想使用自动缓存功能可以修改`settings.py`中的`CACHED_CALL=True`，并在需要自动缓存的函数上加上装饰器
`log_func_call`: 记录发生调用的函数名、参数、执行时间，如果不想记录到日志可以修改`settings.py`中的`LOG_FUNC_CALL=False`

`cached_call`装饰器在`settings.py`中的`CACHED_CALL=True`且被装饰的函数的执行时间大于`CACHED_OVER_EXEC_MILLISECONDS`毫秒时，
会缓存执行结果，namespace为views只缓存view的get请求，为funcs时缓存普通函数。若指定`over_ms`参数，这由该时间来判断是否进行缓存此时`CACHED_OVER_EXEC_MILLISECONDS`无效。
缓存过期时间为`CACHED_EXPIRE_SECONDS`秒。

**日志**

日志默认只在console中打印，要保存到文件需要修改相应的配置

需要记录日志时，使用`utils.log`中的`app_logger`，好处是如果你配置了`SENTRY_DSN`在warning级别以上的日志会被自动被sentry捕获。

**返回JSON命名风格**

如果你的API需要统一JSON字段的命名风格，可以修改`settings.py`中的`JSON_KEYCASE`来动态改变。

默认支持的命名风格有：`camelcase`, `capitalcase`, `constcase`, `lowercase`, `pascalcase`, `pathcase`, `sentencecase`, `snakecase`, `spinalcase`, `titlecase`, `trimcase`, `uppercase`, `alphanumcase`

    camelcase('foo_bar_baz') # => "fooBarBaz"
    camelcase('FooBarBaz') # => "fooBarBaz"
    capitalcase('foo_bar_baz') # => "Foo_bar_baz"
    capitalcase('FooBarBaz') # => "FooBarBaz"
    constcase('foo_bar_baz') # => "FOO_BAR_BAZ"
    constcase('FooBarBaz') # => "_FOO_BAR_BAZ"
    lowercase('foo_bar_baz') # => "foo_bar_baz"
    lowercase('FooBarBaz') # => "foobarbaz"
    pascalcase('foo_bar_baz') # => "FooBarBaz"
    pascalcase('FooBarBaz') # => "FooBarBaz"
    pathcase('foo_bar_baz') # => "foo/bar/baz"
    pathcase('FooBarBaz') # => "/foo/bar/baz"
    sentencecase('foo_bar_baz') # => "Foo bar baz"
    sentencecase('FooBarBaz') # => "Foo bar baz"
    snakecase('foo_bar_baz') # => "foo_bar_baz"
    snakecase('FooBarBaz') # => "_foo_bar_baz"
    spinalcase('foo_bar_baz') # => "foo-bar-baz"
    spinalcase('FooBarBaz') # => "-foo-bar-baz"
    titlecase('foo_bar_baz') # => "Foo Bar Baz"
    titlecase('FooBarBaz') # => " Foo Bar Baz"
    trimcase('foo_bar_baz') # => "foo_bar_baz"
    trimcase('FooBarBaz') # => "FooBarBaz"
    uppercase('foo_bar_baz') # => "FOO_BAR_BAZ"
    uppercase('FooBarBaz') # => "FOOBARBAZ"
    alphanumcase('_Foo., Bar') # =>'FooBar'
    alphanumcase('Foo_123 Bar!') # =>'Foo123Bar'

**JSON参数验证**

使用[cerberus](https://github.com/pyeve/cerberus)进行json参数验证，
所有验证的`validator_schemas`统一存放在对应的蓝图目录下。

**异步任务**

使用celery做异步调用，需要rabbitmq（broker）和redis（backend）服务。

rabbitmq创建vhost

    ./rabbitmqctl add_user username password
    ./rabbitmqctl set_user_tags username administrator
    ./rabbitmqctl add_vhost vhostname
    ./rabbitmqctl set_permissions -p vhostname username ".*" ".*" ".*"

运行worker：`celery worker -A apis.demo.handlers.celery --loglevel=debug -Q send_email`



## Demo

demo示例展示MySQL操作和异步执行任务，
业务代码都可以安装demo结构编写。

查看demo示例以`.env`的当时修改配置文件中的`MYSQL_URL`是否为你当前环境的配置，
导入demo示例的sql文件`v0.0.1.sql`后即可调用接口。接口调用可以访问API文档在线调用测试。


## 部署

直接部署可以使用`deploy\.init.sh`会以supervisor方式运行服务，包括apiserver和各个celery worker。


## 代码结构说明

所有api以blueprint方式按业务目录存放在apis中，在apiserver.py中统一注册。

每一个业务api中，routes.py存放url路由信息，views.py做HTTP动词的业务处理，建议使用Pluggable Views的方式编写view方便按flasgger写docstring，handlers.py存放可复用代码，validator_schemas.py统一存放json验证schema供view使用

使用flask-script编写的快捷命令统一写在manage.py中。

所有model放在models中，每个model内实现一些常用方法，方法内不管理数据库连接，在业务代码中使用`peewee_mysql`上下文管理器来统一处理。

定时任务采用celery beat实现，统一放在`periodic_tasks`目录下

所有依赖的服务都统一放在services.py中。

通用工具类函数统一放在utils下

部署相关的文件、配置等统一放在deploy下。

sqls文件中存放每一个版本涉及到的所有增量sql

## TODO:

- utils
    - statsd
- tests
