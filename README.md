
## Danish Startup Researcher

This is a project that researches Danish startups and their funding activities.

To get started, reference the .example.env file to set up your environment variables.

Then, run the following commands to start the project:

```bash
docker compose up -d
```

this will build the services.

to build a report, you must run the researcher service.

```bash
docker compose up researcher -d
```

this will build the researcher service and run the research flow.

the report will be available in the data/reports/condensed_research.json file.

navigate to the frontend service which is available at <http://localhost:3000>.