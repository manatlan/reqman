# Python powered

Using "params" statement, it possible in introduce python scripts, to make you tests more powerful.

Can be really useful to:

 * transform data (gzip, base64, encrypt, ...)
 * save content
 * compute complex data
 * ...

(You can include all python libs available in reqman, but for others lib you should have python3 on the host with yours libs.)


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
        return zlib.compress( x )

```

And you can chain methods like this

```yaml
- POST: /post
  body: <<content|gzip|b64>>
  params:
    content: "hello world"
    gzip: |
        import zlib
        return zlib.compress( x )
    b65: |
        import base64
        return base64.b64encode( x )
```

A better place for theses methods : declare them in the [reqman.conf](conf.md) !