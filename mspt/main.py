from mspt.init import initialize_mspt
if initialize_mspt():
    from fastapi import FastAPI
    from starlette.middleware.cors import CORSMiddleware
    from starlette.requests import Request
    from fastapi.staticfiles import StaticFiles

    from mspt.settings import config
    from mspt.utils.create_dirs import resolve_root_dirs
    from mspt.api import api_router
    from mspt.settings.database import SessionLocal



    mspt_app = FastAPI(
        title=config.PROJECT_NAME,
        openapi_url=config.API_V1_STR + "/openapi.json")

    # CORS
    origins = []

    # Set all CORS enabled origins
    if config.BACKEND_CORS_ORIGINS:
        origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
        for origin in origins_raw:
            use_origin = origin.strip()
            origins.append(use_origin)
        mspt_app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),


    resolve_root_dirs()
    # app.mount('/static', StaticFiles(directory="static"), name='static')
    mspt_app.mount('/media', StaticFiles(directory="media"), name='media')
    mspt_app.include_router(api_router, prefix=config.API_V1_STR)


    @mspt_app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        request.state.db = SessionLocal()
        response = await call_next(request)
        request.state.db.close()
        return response
