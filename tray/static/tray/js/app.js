function table_grouper(grouping_cell,table_id){
    var table = document.getElementById(table_id);
    console.log(table);
    if (table  === null){
        return;
    }
    var rowLength = table.rows.length;
    console.log("rowlength: "+rowLength);
    var prev_cell = null;
    var prev_follow_cell = null;
    for(let c=2; c<rowLength; c+=1){
        var row = table.rows[c];
        var cellLength = row.cells.length;
        console.log("no of cells in row: "+ cellLength);
        var group_cell = row.cells[grouping_cell];
        if (group_cell === undefined){
            continue;
        }
        console.log(group_cell.innerText);
        console.log('rowspan of it: '+group_cell.rowSpan)

        if (prev_cell === null || group_cell.innerText !== prev_cell.innerText){
            prev_cell = group_cell;
        }
        else {
            prev_cell.rowSpan++;
            console.log('group cell: ' + group_cell)
            group_cell.remove();
        }
        console.log('rowspan final: ' + prev_cell.rowSpan)

    }//end of for loop 
}

function print(){
    alert("function reached!")
}

function checkemail(email) 
    {
        var re = /\S+@\S+\.\S+/;
        return re.test(email);
    }

function follower_cell_grouper(grouping_cell,following_cell){
    var table = document.getElementById('table');
    var rowLength = table.rows.length;
    //alert(rowLength);
    console.log('following cell:' + following_cell)
    console.log('grouping cell:' + grouping_cell)

    for(let j=2; j<rowLength; j++){
        
        var row = table.rows[j];
        var follow_cell = row.cells[following_cell];
        if (follow_cell === undefined){
            continue;
        }
        var group_cell = row.cells[grouping_cell];
        if (group_cell === undefined){
            continue;
        }
        console.log('group cell: ' + group_cell)
        if (group_cell.rowSpan > 1){
            cells_difference = group_cell.rowSpan - follow_cell.rowSpan
            console.log('cell difference:' + cells_difference)
            follow_cell.rowSpan = group_cell.rowSpan
            for(let i=j+1; i<=j+cells_difference; i++){
                console.log('i in j: ' + i)
                console.log('j ' + j)
                drop_row = table.rows[i];
                console.log('drop row: ' + drop_row)
                drop_cell = drop_row.cells[following_cell];
                console.log('drop cell: ' + drop_cell.innerText);
                drop_cell.remove();
                rowLength--;
            }
        }
        
    }
}