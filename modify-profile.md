# Modifying This Profile

This profile is itself in a git repository. Whenever an experiment is
instantiated, that repository is cloned to `/local/repository`. You
can make your own clone of the repository, modify either the resource
allocation geni-lib script or any of the startup or utility scripts,
and create a new profile based on your cloned repository.

### Resource Allocation

The resource allocation script is in `/local/repository/profile.py`
and this Python script is run before the experiment begins to specify the
resources that will be used for the experiment. You could modify it to
add other compute nodes, other radios, or change what scripts are run
at startup.

The geni-lib libraries that are used to build up this resource
specification are described in our
[documentation](http://docs.powderwireless.net/geni-lib.html). Modifying
`profile.py` after an experiment begins won't change the allocated
resources of that experiment.

### Startup Scripts

In `profile.py`, a startup script is specified for the `enb1` and
`epc` nodes. That script is located in
`/local/repository/bin/config_oai.pl`. This script is executed (with
`/the parameters specified in `profile.py`) at experiment startup and
`/every time the experiment boots.

The first time `config_oai.pl` runs, it uses the configuration
templates in `/local/repository/etc/*` to generate configuration files
for all of the OAI services. Then it touches
`/var/emulab/boot/OAI_CONFIG_DONE` so that it won't regenerate those
files on future run-throughs. If you want to regenerate the
configuration files on `enb1` or `epc`, remove
`/var/emulab/boot/OAI_CONFIG_DONE` and rerun `config_oai.pl`.

After generating the configuration files, `config_oai.pl` starts up
all the services in a synchronized way. The instance running on the
`epc` node starts up the MME, HSS, and SPGW and then waits. And the
instance running on the `enb1` node waits until all the other services
are started before beginning the eNodeB. If one is run without the
other, it will wait forever. The `config_oai.pl` script logs its
output to `/var/log/oai/startup.log` in addition to printing it to
standard out.

### Service Scripts

The other scripts in `/local/repository/bin` provide a way to manage
each individual service by hand. They can start or stop any of the OAI
services. There is no synchronization here. Each one of them sets up a
screen session, and also clones their output to log files into a file
in `/var/log/oai`.

### Creating a Profile

While any of these scripts can be modified, the changes won't persist
unless you create your own profile. Go to the portal, select this
profile, and click 'copy'.

A pop-up box will tell you the URL of this repository and you will
need to use that URL to fork this repository using gitlab or github or
some other git hosting service.

Once you have forked the repository, you can paste the URL for the new
repository and then your new profile will point at your new
repository. In order to have the new profile automatically track
changes to the forked repository, you will need to set up a push hook
on the fork.

[Full Documentation on Repository-Based Profiles](http://docs.powderwireless.net/creating-profiles.html#%28part._repo-based-profiles%29)
