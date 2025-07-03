# Dockerfile for Rasa NLU Only
FROM rasa/rasa:3.6.2

# Set working directory
WORKDIR /app

# Copy training data and config
COPY ./config.yml ./
COPY ./data ./data

# Train the Rasa NLU model
RUN rasa train nlu

# Expose port for REST API
EXPOSE 5005

# Run Rasa in NLU-only mode via REST
CMD ["run", "--enable-api", "--model", "models", "--port", "5005", "--cors", "*"]
