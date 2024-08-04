# velux-netatmo-exporter

This is a prometheus exporter to read all window and sensor data from a velux with netatmo gateway (KIX 300)/system.

The velux system is basically a netatmo system with some branched of software stack and own separate server endpoint.
The APIs are however mostly the same as it looks.

This code is more a quick write down so it does not handle errors well.
Also it is not ment to be maintained in the future.
It however works fine for me currently.

## Setup / upsage
Just fill out the `velux.env` file - see `velux_example.env`.
Make sure `/var/lib/velux-netatmo-exporter/token.json` is writable.
Start the python script / or better the container running it.

If you are looking for the clientid or client-secret:
I am hasitant to provide those for legal reasons. sorry.
You can however find all important information to to get those below.

`podman build -t velux-netatmo-exporter .`
`podman run -ti --env-file velux.env -p 9211:9211 velux-netatmo-exporter:latest`
same would to with docker.

## Thanks for the preparatory work and links
Thanks to the ones who investiged before me - I guess that saved me a day of work.
Following are links to helpful projects doing similar things and which were helpful for this project.

### velux client details by hbow
This gave me a very nice short cut to get the client details for the KIX 300.
Thanks man, doing this always takes half a day or a day. This is very much appreciated.

https://community.openhab.org/t/connecting-velux-active-kix-300/75696/41

### velux-cli by nougad
The protocol documentation was very helpful since the official netatmo documentation does not really contain much about velux and one needs to go through and test all the calls.
Also to mention the swagger link.

https://github.com/nougad/velux-cli
https://github.com/nougad/velux-cli/blob/master/velux-protocol.md
https://github.com/nougad/velux-cli/issues/2
https://cbornet.github.io/netatmo-swagger-decl/#operation/getmeasure

### The netatmo exporter by xperimental
This project does export all the netatmo weatherstation sensor data.
At the beginning I wanted to extend it but I did not want to learn go and figured i can do it much faster from scratch in python.
Works for me - sorry ;)

https://github.com/xperimental/netatmo-exporter

### official netatmo docs
It is nice and appreciated that they provide those - but to be honest they could be presented better.

https://dev.netatmo.com/apidocumentation

## velux subdomain links
Good to know links to velux subdomains of interest. Maybe this gets handy at some time.

used for this:
https://app.velux-active.com/
you can log into your account but nothing more:
https://auth.velux-active.com/
not sure what that does:
https://api.velux-active.com/
when logged in via auth you see your gateways settings:
https://settings.velux-active.com/

