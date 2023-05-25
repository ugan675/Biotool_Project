var URL = "{% url 'home' %}";
var term = new Terminal();
var shellprompt = '$ ';
var cmd = "";
var username = "{{user.get_username}}";
var CSRF_TOKEN = '{{ csrf_token }}';
"{% load custom_tags %}";

var decodeEntities = (function() {
    // this prevents any overhead from creating the object each time
    var element = document.createElement('div');

    term.new_line = function() {
        term.write('\r\n');
    };

    term.open(document.getElementById('terminal'), false);

    term.prompt = function() {
        term.write('\r\n' + shellprompt);
    };

    term.writeln('Welcome to xterm.js');
    term.writeln('This is a local terminal emulation, without a real terminal in the back-end.');
    term.writeln('Type some keys and commands to play around.');
    term.writeln('');
    term.prompt();
    term.setOption('cursorBlink', true);



    function decodeHTMLEntities(str) {
        if (str && typeof str === 'string') {
            // strip script/html tags
            str = str.replace(/<script[^>]*>([\S\s]*?)<\/script>/gmi, '');
            str = str.replace(/<\/?\w(?:[^"'>]|"[^"]*"|'[^']*')*>/gmi, '');
            element.innerHTML = str;
            str = element.textContent;
            element.textContent = '';
        }

        return str;
    }

    return decodeHTMLEntities;
})();

function output_results(str) {
    str = str.replace(/\n/g, '\r\n');
    str = str.replace(/\n$/, '');
    term.write(str);
    term.prompt();
}

function updateCommand() {
    $.ajax({
        url: URL,
        type: 'get',
        data: {
            'cmd': cmd
        },
        success: function(response) {
            output_results(response.globalresult);
        }
    })
}

function addcmd(clicked_id) {
    if (username) {
        term.write(clicked_id);
        cmd += clicked_id;
    } else {
        term.write("User not authenticated!");
    }
}

term.on('key', function(key, ev) {
    var printable = (
        !ev.altKey && !ev.altGraphKey && !ev.ctrlKey && !ev.metaKey
    );

    if (ev.keyCode == 13) {
        if (cmd === 'clear') {
            term.clear();
        } else if (cmd === 'upload1') {
            term.prompt();
            term.write(username);
        } else if (cmd) {
            updateCommand();
            cmd = '';
        }
        term.new_line();
        cmd = '';
    } else if (ev.keyCode == 8) {
        if (cmd) {
            term.write('\b \b');
            cmd = cmd.slice(0, -1);
        }
    } else if (printable) {
        cmd += key;
        term.write(key);
    }
});

term.on('paste', function(data, ev) {
    term.write(data);
});