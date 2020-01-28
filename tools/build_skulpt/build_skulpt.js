const OUTPUT_FILE = "../../dist/skulpt-pedal.js";
const SOURCE_DIRS = ['../../pedal', "../../CS1014"]; // No trailing slash

const skulpt = require("../../../blockpy-edu/skulpt/dist/skulpt.js");
Sk.configure({__future__: Sk.python3});

const fs = require('fs');
const path = require('path');
const minify = require('babel-minify');
const beautify = require('js-beautify');

function buildPythonFile(ret, fullname, contents) {
    var internalName = fullname;
    while (internalName.startsWith("../")) {
        internalName = internalName.slice(3);
    }
    internalName = "src/lib/"+internalName;
    try {
        co = Sk.compile(contents, internalName, "exec", true, false);
        console.log("Compiled: "+internalName);
    } catch (e) {
        console.log("Failed to compile: "+internalName);
        console.log(e);
        console.log(e.stack);
        console.error(e.args);
    }
    internalName = internalName.replace(/\.py$/, ".js");
    contents = co.code + "\nvar $builtinmodule = " + co.funcname + ";";
    contents = minify(contents).code;
    ret[internalName] = contents;
}

function processDirectories(dirs, recursive, exts, ret, minifyjs, excludes) {
    dirs.forEach((dir) => {
        let files = fs.readdirSync(dir);

        files.forEach((file) => {
            let fullname = dir + '/' + file;

            if (!excludes.includes(fullname)) {
                let stat = fs.statSync(fullname);

                if (recursive && stat.isDirectory()) {
                    processDirectories([fullname], recursive, exts, ret, minifyjs, excludes);
                } else if (stat.isFile()) {
                    let ext = path.extname(file);
                    if (exts.includes(ext)) {
                        let contents = fs.readFileSync(fullname, "utf8");
                        if (ext === ".py") {
                            buildPythonFile(ret, fullname, contents);
                        }
                    }
                }
            }
        });
    });
}

var dirs = SOURCE_DIRS;
var result = {};
processDirectories(dirs, true, '.py', result, true, []);
let output = [];
for (let filename in result) {
    let contents = result[filename];
    output.push("Sk.builtinFiles.files['"+filename+"'] = "+JSON.stringify(contents));
}
fs.writeFileSync(OUTPUT_FILE, output.join("\n"), 'utf8');

console.log(Object.keys(result));