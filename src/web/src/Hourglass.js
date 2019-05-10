import React from "react";

import hourglass from "./hourglass.gif";
import brokenglass from "./brokenglass.png";

function Hourglass(props) {
    return (
      <div class="hourglass text-center">
        <img src={props.hourglass || hourglass} alt="hourglass" width="200px"/>
        <h3>{props.message}</h3>
      </div>
    )
}

export {
    Hourglass,
    hourglass,
    brokenglass
}