           ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3278, in connect  
    return self._connection_cls(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__  
    self._dbapi_connection = engine.raw_connection()  
                             ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3302, in raw_connection  
    return self.pool.connect()  
           ^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect  
    return _ConnectionFairy._checkout(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout  
    fairy = _ConnectionRecord.checkout(pool)  
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout  
    rec = pool._do_get()  
          ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get  
    return self._create_connection()  
           ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection  
    return _ConnectionRecord(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__  
    self.__connect()  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect  
    with util.safe_reraise():  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__  
    raise exc_value.with_traceback(exc_tb)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect  
    self.dbapi_connection = connection = pool._invoke_creator(self)  
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect  
    return dialect.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 621, in connect  
    return self.loaded_dbapi.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 949, in connect  
    await_only(creator_fn(*arg, **kw)),  
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only  
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn  
    value = await result  
            ^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connection.py", line 2421, in connect  
    return await connect_utils._connect(  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1049, in _connect  
    conn = await _connect_addr(  
           ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 891, in _connect_addr  
    return await __connect_addr(params_retry, False, *args)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 934, in __connect_addr  
    await connected  
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "ai_avangard_admin"  
Skipping data after last boundary  
INFO:     94.230.230.238:0 - "POST /documents/upload?visibility=private HTTP/1.1" 500 Internal Server Error  
ERROR:    Exception in ASGI application  
Traceback (most recent call last):  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 401, in run_asgi  
    result = await app(  # type: ignore[func-returns-value]  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__  
    return await self.app(scope, receive, send)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__  
    await super().__call__(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/applications.py", line 113, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 187, in __call__  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__  
    await self.app(scope, receive, _send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 93, in __call__  
    await self.simple_response(scope, receive, send, request_headers=headers)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 144, in simple_response  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__  
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 715, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 735, in app  
    await route.handle(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 76, in app  
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 73, in app  
    response = await f(request)  
               ^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/routing.py", line 291, in app  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 628, in solve_dependencies  
    solved = await call(**solved_result.values)  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/backend/app/middleware/auth.py", line 53, in get_current_user  
    result = await db.execute(select(User).where(User.id == user_id))  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 461, in execute  
    result = await greenlet_spawn(  
             ^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn  
    result = context.throw(*sys.exc_info())  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2362, in execute  
    return self._execute_internal(  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2237, in _execute_internal  
    conn = self._connection_for_bind(bind)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2106, in _connection_for_bind  
    return trans._connection_for_bind(engine, execution_options)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "<string>", line 2, in _connection_for_bind  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go  
    ret_value = fn(self, *arg, **kw)  
                ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind  
    conn = bind.connect()  
           ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3278, in connect  
    return self._connection_cls(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__  
    self._dbapi_connection = engine.raw_connection()  
                             ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3302, in raw_connection  
    return self.pool.connect()  
           ^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect  
    return _ConnectionFairy._checkout(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout  
    fairy = _ConnectionRecord.checkout(pool)  
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout  
    rec = pool._do_get()  
          ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get  
    return self._create_connection()  
           ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection  
    return _ConnectionRecord(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__  
    self.__connect()  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect  
    with util.safe_reraise():  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__  
    raise exc_value.with_traceback(exc_tb)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect  
    self.dbapi_connection = connection = pool._invoke_creator(self)  
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect  
    return dialect.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 621, in connect  
    return self.loaded_dbapi.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 949, in connect  
    await_only(creator_fn(*arg, **kw)),  
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only  
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn  
    value = await result  
            ^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connection.py", line 2421, in connect  
    return await connect_utils._connect(  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1049, in _connect  
    conn = await _connect_addr(  
           ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 891, in _connect_addr  
    return await __connect_addr(params_retry, False, *args)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 934, in __connect_addr  
    await connected  
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "ai_avangard_admin"  
INFO:     94.230.230.238:0 - "GET /admin/users/pending HTTP/1.1" 500 Internal Server Error  
ERROR:    Exception in ASGI application  
Traceback (most recent call last):  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 401, in run_asgi  
    result = await app(  # type: ignore[func-returns-value]  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__  
    return await self.app(scope, receive, send)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__  
    await super().__call__(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/applications.py", line 113, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 187, in __call__  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__  
    await self.app(scope, receive, _send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 85, in __call__  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__  
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 715, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 735, in app  
    await route.handle(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 76, in app  
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 73, in app  
    response = await f(request)  
               ^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/routing.py", line 291, in app  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 605, in solve_dependencies  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 628, in solve_dependencies  
    solved = await call(**solved_result.values)  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/backend/app/middleware/auth.py", line 53, in get_current_user  
    result = await db.execute(select(User).where(User.id == user_id))  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 461, in execute  
    result = await greenlet_spawn(  
             ^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn  
    result = context.throw(*sys.exc_info())  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2362, in execute  
    return self._execute_internal(  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2237, in _execute_internal  
    conn = self._connection_for_bind(bind)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2106, in _connection_for_bind  
    return trans._connection_for_bind(engine, execution_options)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "<string>", line 2, in _connection_for_bind  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go  
    ret_value = fn(self, *arg, **kw)  
                ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind  
    conn = bind.connect()  
           ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3278, in connect  
    return self._connection_cls(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__  
    self._dbapi_connection = engine.raw_connection()  
                             ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3302, in raw_connection  
    return self.pool.connect()  
           ^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect  
    return _ConnectionFairy._checkout(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout  
    fairy = _ConnectionRecord.checkout(pool)  
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout  
    rec = pool._do_get()  
          ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get  
    return self._create_connection()  
           ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection  
    return _ConnectionRecord(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__  
    self.__connect()  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect  
    with util.safe_reraise():  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__  
    raise exc_value.with_traceback(exc_tb)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect  
    self.dbapi_connection = connection = pool._invoke_creator(self)  
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect  
    return dialect.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 621, in connect  
    return self.loaded_dbapi.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 949, in connect  
    await_only(creator_fn(*arg, **kw)),  
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only  
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn  
    value = await result  
            ^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connection.py", line 2421, in connect  
    return await connect_utils._connect(  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1049, in _connect  
    conn = await _connect_addr(  
           ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 891, in _connect_addr  
    return await __connect_addr(params_retry, False, *args)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 934, in __connect_addr  
    await connected  
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "ai_avangard_admin"  
Skipping data after last boundary  
INFO:     94.230.230.238:0 - "POST /documents/upload?visibility=organization HTTP/1.1" 500 Internal Server Error  
ERROR:    Exception in ASGI application  
Traceback (most recent call last):  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 401, in run_asgi  
    result = await app(  # type: ignore[func-returns-value]  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__  
    return await self.app(scope, receive, send)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__  
    await super().__call__(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/applications.py", line 113, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 187, in __call__  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__  
    await self.app(scope, receive, _send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 93, in __call__  
    await self.simple_response(scope, receive, send, request_headers=headers)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 144, in simple_response  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__  
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 715, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 735, in app  
    await route.handle(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 76, in app  
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 73, in app  
    response = await f(request)  
               ^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/routing.py", line 291, in app  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 628, in solve_dependencies  
    solved = await call(**solved_result.values)  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/backend/app/middleware/auth.py", line 53, in get_current_user  
    result = await db.execute(select(User).where(User.id == user_id))  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 461, in execute  
    result = await greenlet_spawn(  
             ^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn  
    result = context.throw(*sys.exc_info())  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2362, in execute  
    return self._execute_internal(  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2237, in _execute_internal  
    conn = self._connection_for_bind(bind)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2106, in _connection_for_bind  
    return trans._connection_for_bind(engine, execution_options)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "<string>", line 2, in _connection_for_bind  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go  
    ret_value = fn(self, *arg, **kw)  
                ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind  
    conn = bind.connect()  
           ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3278, in connect  
    return self._connection_cls(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__  
    self._dbapi_connection = engine.raw_connection()  
                             ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3302, in raw_connection  
    return self.pool.connect()  
           ^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect  
    return _ConnectionFairy._checkout(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout  
    fairy = _ConnectionRecord.checkout(pool)  
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout  
    rec = pool._do_get()  
          ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get  
    return self._create_connection()  
           ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection  
    return _ConnectionRecord(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__  
    self.__connect()  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect  
    with util.safe_reraise():  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__  
    raise exc_value.with_traceback(exc_tb)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect  
    self.dbapi_connection = connection = pool._invoke_creator(self)  
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect  
    return dialect.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 621, in connect  
    return self.loaded_dbapi.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 949, in connect  
    await_only(creator_fn(*arg, **kw)),  
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only  
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn  
    value = await result  
            ^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connection.py", line 2421, in connect  
    return await connect_utils._connect(  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1049, in _connect  
    conn = await _connect_addr(  
           ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 891, in _connect_addr  
    return await __connect_addr(params_retry, False, *args)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 934, in __connect_addr  
    await connected  
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "ai_avangard_admin"  
INFO:     94.230.230.238:0 - "GET /admin/users/pending HTTP/1.1" 500 Internal Server Error  
ERROR:    Exception in ASGI application  
Traceback (most recent call last):  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 401, in run_asgi  
    result = await app(  # type: ignore[func-returns-value]  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__  
    return await self.app(scope, receive, send)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__  
    await super().__call__(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/applications.py", line 113, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 187, in __call__  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__  
    await self.app(scope, receive, _send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 85, in __call__  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__  
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 715, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 735, in app  
    await route.handle(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 76, in app  
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 73, in app  
    response = await f(request)  
               ^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/routing.py", line 291, in app  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 605, in solve_dependencies  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 628, in solve_dependencies  
    solved = await call(**solved_result.values)  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/backend/app/middleware/auth.py", line 53, in get_current_user  
    result = await db.execute(select(User).where(User.id == user_id))  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 461, in execute  
    result = await greenlet_spawn(  
             ^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn  
    result = context.throw(*sys.exc_info())  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2362, in execute  
    return self._execute_internal(  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2237, in _execute_internal  
    conn = self._connection_for_bind(bind)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2106, in _connection_for_bind  
    return trans._connection_for_bind(engine, execution_options)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "<string>", line 2, in _connection_for_bind  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go  
    ret_value = fn(self, *arg, **kw)  
                ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind  
    conn = bind.connect()  
           ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3278, in connect  
    return self._connection_cls(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__  
    self._dbapi_connection = engine.raw_connection()  
                             ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3302, in raw_connection  
    return self.pool.connect()  
           ^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect  
    return _ConnectionFairy._checkout(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout  
    fairy = _ConnectionRecord.checkout(pool)  
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout  
    rec = pool._do_get()  
          ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get  
    return self._create_connection()  
           ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection  
    return _ConnectionRecord(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__  
    self.__connect()  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect  
    with util.safe_reraise():  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__  
    raise exc_value.with_traceback(exc_tb)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect  
    self.dbapi_connection = connection = pool._invoke_creator(self)  
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect  
    return dialect.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 621, in connect  
    return self.loaded_dbapi.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 949, in connect  
    await_only(creator_fn(*arg, **kw)),  
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only  
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn  
    value = await result  
            ^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connection.py", line 2421, in connect  
    return await connect_utils._connect(  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1049, in _connect  
    conn = await _connect_addr(  
           ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 891, in _connect_addr  
    return await __connect_addr(params_retry, False, *args)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 934, in __connect_addr  
    await connected  
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "ai_avangard_admin"  
INFO:     94.230.230.238:0 - "GET /admin/users/pending HTTP/1.1" 500 Internal Server Error  
ERROR:    Exception in ASGI application  
Traceback (most recent call last):  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 401, in run_asgi  
    result = await app(  # type: ignore[func-returns-value]  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__  
    return await self.app(scope, receive, send)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__  
    await super().__call__(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/applications.py", line 113, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 187, in __call__  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__  
    await self.app(scope, receive, _send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 85, in __call__  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__  
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 715, in __call__  
    await self.middleware_stack(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 735, in app  
    await route.handle(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle  
    await self.app(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 76, in app  
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 62, in wrapped_app  
    raise exc  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 51, in wrapped_app  
    await app(scope, receive, sender)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/starlette/routing.py", line 73, in app  
    response = await f(request)  
               ^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/routing.py", line 291, in app  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 605, in solve_dependencies  
    solved_result = await solve_dependencies(  
                    ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/fastapi/dependencies/utils.py", line 628, in solve_dependencies  
    solved = await call(**solved_result.values)  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/backend/app/middleware/auth.py", line 53, in get_current_user  
    result = await db.execute(select(User).where(User.id == user_id))  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/session.py", line 461, in execute  
    result = await greenlet_spawn(  
             ^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn  
    result = context.throw(*sys.exc_info())  
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2362, in execute  
    return self._execute_internal(  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2237, in _execute_internal  
    conn = self._connection_for_bind(bind)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 2106, in _connection_for_bind  
    return trans._connection_for_bind(engine, execution_options)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "<string>", line 2, in _connection_for_bind  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go  
    ret_value = fn(self, *arg, **kw)  
                ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind  
    conn = bind.connect()  
           ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3278, in connect  
    return self._connection_cls(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__  
    self._dbapi_connection = engine.raw_connection()  
                             ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3302, in raw_connection  
    return self.pool.connect()  
           ^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect  
    return _ConnectionFairy._checkout(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout  
    fairy = _ConnectionRecord.checkout(pool)  
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout  
    rec = pool._do_get()  
          ^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get  
    return self._create_connection()  
           ^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection  
    return _ConnectionRecord(self)  
           ^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__  
    self.__connect()  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect  
    with util.safe_reraise():  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__  
    raise exc_value.with_traceback(exc_tb)  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect  
    self.dbapi_connection = connection = pool._invoke_creator(self)  
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect  
    return dialect.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 621, in connect  
    return self.loaded_dbapi.connect(*cargs, **cparams)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 949, in connect  
    await_only(creator_fn(*arg, **kw)),  
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only  
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn  
    value = await result  
            ^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connection.py", line 2421, in connect  
    return await connect_utils._connect(  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1049, in _connect  
    conn = await _connect_addr(  
           ^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 891, in _connect_addr  
    return await __connect_addr(params_retry, False, *args)  
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  
  File "/home/temrjan/ai-avangard/venv/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 934, in __connect_addr  
    await connected  
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "ai_avangard_admin"  
