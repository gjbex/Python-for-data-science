---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.5.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# City centers


## Reading files


Load the required modules

```python
import geopandas as gpd
%matplotlib inline
```

Load a GeoJSON file containing GeoJSON file.

```python
belgium = gpd.read_file('https://gist.githubusercontent.com/jandot/ba7eff2e15a38c6f809ba5e8bd8b6977/raw/eb49ce8dd2604e558e10e15d9a3806f114744e80/belgium_municipalities_topojson.json')
```

Get info on the dataframe.

```python
belgium.info()
```

Set the municipaolities `CODE_INS` as the index for the dataframe.

```python
belgium.set_index('CODE_INS', inplace=True)
```

Find the entry for Hasselt.

```python
belgium.query('ADMUNADU == "HASSELT"')
```

Get the geomerty for Belgium. It is returned as a Shapely object, a `Polygon` in this case.

```python
hasselt_shape = belgium.at['71022', 'geometry']
```

```python
hasselt_shape
```

## Centroids


Although it is possible to obtain the coordinates of city centers online, this data is not freely available.  We can approximate the location by computing the centroid of the geometric shape associdatted with the municipality.

```python
hasselt_shape.centroid
```

```python
belgium['center'] = belgium.geometry.centroid
```

```python
belgium
```

Write the coordinates to a JSON file.

```python
with open('Data/city_centers.json', 'w') as file:
    print(gpd.GeoSeries(belgium.center).to_json(), file=file)
```

Plot the centers on top of the map of Belgium.

```python
centers = gpd.GeoDataFrame(geometry=belgium.center)
```

```python
axes = centers.plot(markersize=1, color='red', figsize=(12, 15))
_ = belgium.geometry.plot(ax=axes, color='white', edgecolor='black', alpha=0.5)
```

```python
centers['longitude'] = centers.geometry.x
centers['latitude'] = centers.geometry.y
```

```python
centers.info()
```

```python
centers[['longitude', 'latitude']].to_csv('Data/city_centers.csv')
```
