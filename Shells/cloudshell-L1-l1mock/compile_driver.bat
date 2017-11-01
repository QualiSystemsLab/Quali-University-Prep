pyinstaller --onefile driver.spec
copy datamodel\*.xml dist /Y
copy l1mock_runtime_configuration.json dist /Y
