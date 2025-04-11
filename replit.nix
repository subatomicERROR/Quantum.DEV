{ 
  "language": "nix", 
  "packages": [ 
    "python310", 
    "nodejs" 
  ], 
  "shell": { 
    "buildInputs": [ 
      "python310", 
      "python310Packages.fastapi", 
      "python310Packages.requests", 
      "python310Packages.python-dotenv", 
      "python310Packages.uvicorn", 
      "nodejs" 
    ] 
  } 
}