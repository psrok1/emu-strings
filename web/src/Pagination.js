import React from 'react';

export default function Pagination(props) {
    let isDisabled = props.disabled;
    let hasPrevious = props.page > 1;
    let hasMore = props.hasMore;
    let pageItemClass = (condition, active) => `page-item ${!condition ? "disabled" : (active ? "active" : "")}`


    function handler(fn) {
        return ev => {ev.preventDefault(); isDisabled || fn();}
    }

    return (
        <nav>
            <ul class="pagination justify-content-center">
                <li class={pageItemClass(!isDisabled && hasPrevious)}>
                    <a class="page-link" 
                       href="#prev" 
                       tabindex="-1"
                       onClick={handler(props.previous)}>
                        Previous
                    </a>
                </li>
                {
                    hasPrevious ?
                    <li class={pageItemClass(!isDisabled)}>
                        <a class="page-link" 
                           href="#prev"
                           onClick={handler(props.previous)}>
                            {props.page - 1}
                        </a>
                    </li>
                    : []
                }
                {
                    props.page > 0 ?
                    <li class={pageItemClass(!isDisabled, true)}>
                        <a class="page-link" 
                        href="#current"
                        onClick={handler(()=>{})}>
                        {props.page}
                        </a>
                    </li>
                    : []
                }
                {
                    hasMore ?
                    <li class={pageItemClass(!isDisabled)}>
                        <a class="page-link" 
                           href="#next"
                           onClick={handler(props.next)}>
                            {props.page + 1}
                        </a>
                    </li>
                    : []
                }
                <li class={pageItemClass(!isDisabled && hasMore)}>
                    <a class="page-link" 
                       href="#next"
                       onClick={handler(props.next)}>
                       Next
                    </a>
                </li>
            </ul>
        </nav>
    );
}