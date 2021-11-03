from app.config.app_config import conf


def get_resource_id_from_user_id(item_id: str) -> str:
    return f"{conf.RESOURCE_NAME_USER}{item_id}"


def get_user_id_from_resource_id(resource_id: str) -> str:
    if resource_id.startswith(conf.RESOURCE_NAME_USER):
        return resource_id[len(conf.RESOURCE_NAME_USER) :]
    else:
        raise Exception("resource id not starting with resource name..")