from pydantic2ts import generate_typescript_defs

generate_typescript_defs("backend.metadata.types", "./frontend/src/typesGenerated.ts")