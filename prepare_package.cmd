echo off

echo pack shells
cd Shells
cd putshell
shellfoundry pack
copy dist\putshell.zip "..\..\Blueprints\Admin Blueprint\Scripts\Admin Setup Script\putshell.zip" /y
cd ..
cd trafficshell
shellfoundry pack
copy dist\trafficshell.zip "..\..\Blueprints\Admin Blueprint\Scripts\Admin Setup Script\trafficshell.zip" /y
cd ..
cd l2mockswitch
shellfoundry pack
copy dist\l2mockswitch.zip "..\..\Blueprints\Admin Blueprint\Scripts\Admin Setup Script\l2mockswitch.zip" /y
cd ..\..

echo pack put traffic blueprint
cd "Blueprints\PUT Traffic Test Blueprint\Scripts"
cd Setup
del *.zip
"c:\Program Files\7-Zip\7z.exe" a "..\..\Package\Topology Scripts\Setup Training.zip" *
cd..
cd Teardown
del *.zip
"c:\Program Files\7-Zip\7z.exe" a "..\..\Package\Topology Scripts\Teardown Training.zip" *
cd..
cd "Run Tests"
copy "Run Tests.py" "..\..\Package\Topology Scripts" /y
cd..\..\..\..
cd "Blueprints\PUT Traffic Test Blueprint\Package"
del *.zip
del "..\..\..\Blueprints\Admin Blueprint\Scripts\Admin Setup Script\PUT Traffic Test Blueprint.zip"
"c:\Program Files\7-Zip\7z.exe" a "..\..\..\Blueprints\Admin Blueprint\Scripts\Admin Setup Script\PUT Traffic Test Blueprint.zip" *
cd..\..\..

echo pack admin setup script
cd "Blueprints\Admin Blueprint\Scripts\Admin Setup Script"
del "..\..\Package\topology scripts\Admin Setup Script.zip"
"c:\Program Files\7-Zip\7z.exe" a "..\..\Package\topology scripts\Admin Setup Script.zip" *
cd..\..\..\..

echo pack admin blueprint
cd "Blueprints\Admin Blueprint\Package"
del *.zip
"c:\Program Files\7-Zip\7z.exe" a "..\..\..\Packages\Admin Blueprint.zip" *
cd..\..\..

echo deleting files used in the process
cd "Blueprints\Admin Blueprint\Scripts\Admin Setup Script"
del "PUT Traffic Test Blueprint.zip"
del putshell.zip
del trafficshell.zip
del l2mockswitch.zip
cd..\..\..\..
del "Shells\putshell\PutshellDriver.zip"
del "Shells\Trafficshell\Trafficshelldriver.zip"
del "Blueprints\Admin Blueprint\Package\topology scripts\Admin Setup Script.zip"

echo done

