echo off

echo pack shells
cd Shells
cd putshell
shellfoundry pack
copy dist\putshell.zip "..\..\Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script\putshell.zip" /y
cd ..
cd trafficshell
shellfoundry pack
copy dist\trafficshell.zip "..\..\Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script\trafficshell.zip" /y
cd ..
cd l2mockswitch
shellfoundry pack
copy dist\l2mockswitch.zip "..\..\Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script\l2mockswitch.zip" /y
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
del "..\..\..\Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script\PUT Traffic Test Blueprint.zip"
"c:\Program Files\7-Zip\7z.exe" a "..\..\..\Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script\PUT Traffic Test Blueprint.zip" *
copy "..\..\..\Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script\PUT Traffic Test Blueprint.zip" "..\PUT Traffic Test Blueprint Package.zip" /y
cd..\..\..

echo pack prep setup script
cd "Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script"
del "..\..\Package\topology scripts\Blueprint Designer Prep Setup Script.zip"
"c:\Program Files\7-Zip\7z.exe" a "..\..\Package\topology scripts\Blueprint Designer Prep Setup Script.zip" *
cd..\..\..\..

echo pack Blueprint Designer Preparations
cd "Blueprints\Blueprint Designer Preparations\Package"
del *.zip
"c:\Program Files\7-Zip\7z.exe" a "..\..\..\Packages\Blueprint Designer Preparations Package.zip" *
cd..\..\..

echo deleting files used in the process
cd "Blueprints\Blueprint Designer Preparations\Scripts\Prep Setup Script"
del "PUT Traffic Test Blueprint.zip"
del putshell.zip
del trafficshell.zip
del l2mockswitch.zip
cd..\..\..\..
del "Shells\putshell\PutshellDriver.zip"
del "Shells\Trafficshell\Trafficshelldriver.zip"
del "Shells\l2mockswitch\l2mockswitchdriver.zip"
del "Blueprints\Blueprint Designer Preparations\Package\topology scripts\Blueprint Designer Prep Setup Script.zip"

echo done

