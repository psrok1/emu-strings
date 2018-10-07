const child_process = require('child_process');
const fs = require("fs");

child_process.execFileSync("node", ["/opt/emulator/box-js/run.js", 
                                    "--loglevel", "debug", 
                                    "--timeout", process.env.SOFT_TIMEOUT,
                                    process.env.SAMPLE], {
    cwd: "/opt/analysis",
    timeout: (+process.env.HARD_TIMEOUT)*1000
})

fs.symlinkSync("./"+process.env.SAMPLE+".results", "results")
