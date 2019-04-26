import React from "react";

let STATUS_PENDING = "pending"
let STATUS_IN_PROGRESS = "in-progress"
let STATUS_SUCCESS = "success"
let STATUS_FAILED = "failed"
let STATUS_ORPHANED = "orphaned"

export default function AnalysisStatus(props) {
    let className = {
        [STATUS_PENDING]: "text-secondary",
        [STATUS_IN_PROGRESS]: "text-primary",
        [STATUS_SUCCESS]: "text-success",
        [STATUS_FAILED]: "text-danger",
        [STATUS_ORPHANED]: "text-muted"
    }
    let status = props.status, statusText;
    if(status === STATUS_IN_PROGRESS)
        statusText = "in progress";
    else
        statusText = status;
    return <span className={className[status]}>{statusText}</span>
}

export {
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_SUCCESS,
    STATUS_FAILED,
    STATUS_ORPHANED
}