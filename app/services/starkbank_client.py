import starkbank
from app.core.config import settings, Environment


def get_starkbank_user():
    private_key = settings.STARKBANK_USER_PRIVATE_KEY

    if settings.ENVIRONMENT == Environment.PRODUCTION:
        starkbank_environment = "production"
    else:
        starkbank_environment = "sandbox"

    project = starkbank.Project(
        environment=starkbank_environment,
        id=settings.STARKBANK_PROJECT_ID,
        private_key=private_key
    )
    starkbank.user = project

    return starkbank.user
