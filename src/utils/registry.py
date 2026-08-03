import joblib

def save_model(model, model_name):
    joblib.dump(model, model_name)

def upload_model(project, model_name, model_file_path,version, metrics, description):
    mr = project.get_model_registry()
    model_meta = mr.python.create_model(
        name=model_name,
        version=version,
        metrics=metrics,
        description=description
    )
    model_meta.save(model_file_path)

    print(f"Model {model_name} version {version} uploaded to Hopsworks")