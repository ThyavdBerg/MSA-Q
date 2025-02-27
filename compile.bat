
SET OSGEO4W_ROOT=D:\OSGeo4W
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%
path %PATH%;%OSGEO4W_ROOT%\bin\

call "%OSGEO4W_ROOT%"\bin\o4w_env.bat

@echo on
pyrcc5 -o resources.py resources.qrc
