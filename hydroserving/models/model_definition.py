class ModelDefinition:
    def __init__(self, name, model_type, contract_path, payload, description, is_system, profile_fields):
        self.name = name
        self.model_type = model_type
        self.contract_path = contract_path
        self.payload = payload
        self.description = description
        self.is_system = is_system
        self.profile_fields = profile_fields

    @staticmethod
    def from_dict(data_dict):
        if data_dict is None:
            return None
        return ModelDefinition(
            name=data_dict.get("name"),
            model_type=data_dict.get("type"),
            contract_path=data_dict.get("contract"),
            payload=data_dict.get("payload"),
            description=data_dict.get("description"),
            is_system=data_dict.get("is_system"),
            profile_fields=data_dict.get("profile_fields")
        )
