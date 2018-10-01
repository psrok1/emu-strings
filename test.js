WScript.Quit(1)
var shapp = new ActiveXObject('Shell.Application');
var startup = shapp['NameSpace'](7);
WScript.echo("======DEBUG=======");
WScript.echo(typeof startup);
WScript.echo(typeof startup.Self);
WScript.echo("======DEBUG=======");
