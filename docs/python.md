# Python powered

Using "params" statement, it's possible to embbed python3 scripts, to make your tests more powerful.

Can be really useful to:

 * transform data (gzip, base64, encrypt, ...)
 * save/read content from filesystem
 * compute complex data
 * ...

!!! info
    You can include all python libs available in reqman, but for others libs you should have python3 on the host with yours libs.


## With param value

```yaml
- POST: /post
  body: <<content>>
  params:
    content: |
        with open("image.jpg","rb") as fid:
            return fid.read()
```


## With method over a param value

it's like a param, but 'x' is the input parameter (ENV dict is also available)

```yaml
- POST: /post
  body: <<content|gzip>>
  params:
    content: "hello world"
    gzip: |
        import zlib
        return zlib.compress( bytes(x,"utf8") )
```

And you can chain methods like this

```yaml
- POST: /post
  body: <<content|gzip|b64>>
  params:
    content: "hello world"
    gzip: |
        import zlib
        return zlib.compress( bytes(x,"utf8") )
    b64: |
        import base64
        return str( base64.b64encode( bytes(x,"utf8") ), "utf8" )
```

Example of using a python method to save content during tests:

```yaml
- get: /image.jpeg
  params:
    mysave: |
        with open("myfile.jpg","wb+") as fid:
          fid.write( x )
        return True
  save:
    isSaved: <<content|mysave>>
```

!!! warning
    You will need version >= 2.2.3.0 (previous was bugged ;-( ) 


!!! tip
    A better place for theses methods : declare them in the [reqman.conf](conf.md) !