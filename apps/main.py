import uvicorn
from argparse import ArgumentParser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.dis_api import router as dis_api_module

# Create FastAPI app
app = FastAPI()

# Load FastAPI routers from the various modules
app.include_router(dis_api_module)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_args(debug=False):
    parser = ArgumentParser()
    parser.add_argument(
        "--uvicorn", type=bool, default=False,
        help="Run single worker Uvicorn or "
             "multi workers with Gunicorn"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0",
        help="Host IP address."
    )
    parser.add_argument(
        "--port", type=int, default=9001,
        help="Service port number."
    )

    if debug:
        argv = ["--host", '0.0.0.0', "--port", '8000', "--uvicorn", "TRUE"]
        return parser.parse_args(argv)
    else:
        return parser.parse_args()


@app.get('/')
async def root():
    return {'message': 'Welcome to DIS API.'}


app.mount('/dis_api', dis_api_module)


if __name__ == '__main__':
    args = get_args(debug=True)
    print("Running")
    if args.uvicorn is True:
        print("running uvicorn")
        uvicorn.run(app, host=args.host, port=args.port)
