from pydantic2ts import generate_typescript_defs  # type: ignore

generate_typescript_defs("backend.metadata.types", "./frontend/src/typesGenerated.ts")
