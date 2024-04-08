import uix
from uix.elements import button, page, grid, col, row, text, div
from uix.pipes import status_pipe
uix.html.add_css("sudoku_main","""
button {
    min-width: 50px;
}
.celltext {
    font-size: 14px;
    padding: 1px;
    text-align: center;
    color: #666;
}
.celltext2 {
    font-size: 34px;
    padding: 6px;
    text-align: center;
    color: #fff;
}
.selected {
    background-color: #ccc;
}
.calculated {
    color: blue;
}
.removed {
    color: var(--background)
} 
.highlight {
    background-color: #007;
}
.board {
    display: grid;
    padding: 20px;
    width: 500px;
    height: 600px;
    grid-column-start: 1;
    grid-column-end: 1;
    grid-row-start: 1;
    grid-row-end: 1;
}
.bigcell {
    display: grid;
    border: 2px solid white;
    grid-column-start: 1;
    grid-column-end: 1;
    grid-row-start: 1;
    grid-row-end: 1;
}
.cell {
    border: 1px solid white;
    padding: 5px;
    align-content: center;
    text-align: center;
    width: 50px;
    height: 50px;
}
.cell:hover {
    background-color: #aaa;
}
.cell:hover:active {
    background-color: #eee;
}
""")
pv = [i for i in range(9)]
print(pv)
show_indexes = False
show_highlight = False
selected = -1
class cell(uix.Element):
    def __init__(self, id, value=None):
        super().__init__(id = str(id), value = value)
        self.possibles = pv.copy()
        self.calculated = False
        with self.on("click",self.on_click).cls("cell selected" if selected == self.id else "cell"):
            self.render_numbers()

    def render_numbers(self):
        global show_indexes
        if show_indexes:
            text(value=str(self.id)).cls("celltext2")
            return 
        if len(self.possibles) == 1:
            if self.calculated:
                text(value=str(self.possibles[0]+1)).cls("celltext2").cls("calculated")
            else:
                text(value=str(self.possibles[0]+1)).cls("celltext2")
        else:
            with grid(columns="1fr 1fr 1fr"):
                for i in range(9):
                    if i in self.possibles:
                        text(value=str(i+1)).cls("celltext")
                    else:
                        text(value=str(i+1)).cls("celltext").cls("removed")

    def on_click(self,ctx,id,value):
        global selected
        print(f"cell {self.id} clicked") 
        for i in range(9):
            if i in self.possibles:
                ctx.elements[f"btn-{i}"].set_attr("disabled",False)
            else:
                ctx.elements[f"btn-{i}"].set_attr("disabled",True)      
        calc_possibilities(ctx, self.id)
        if selected != -1:
            ctx.elements[str(selected)].remove_class("selected")
        selected = str(id)
        ctx.elements[str(selected)].add_class("selected")

def bigcell(index):
    with div():
        with grid(columns="1fr 1fr 1fr").cls("bigcell"):
            for i in range(9):
                cell(id = i + index * 9)

dirty_cells = []

def calc_possibilities(ctx,index):
    global dirty_cells
    dirty_cells = [index]
    while len(dirty_cells) > 0:
        index = dirty_cells.pop()
        calc_possibilities_by_index(ctx, index)
    while True:
        for i in range(9):
            ary = get_nearby_cells(i)
            check_single_possibility(ctx, ary)
            ary = get_row_cells(i)
            check_single_possibility(ctx, ary)
            ary = get_col_cells(i)
            check_single_possibility(ctx, ary)
        if len(dirty_cells) > 0:
            while len(dirty_cells) > 0:
                index = dirty_cells.pop()
                calc_possibilities_by_index(ctx, index)
        else:
            break

def remove_possibility_from_array(ctx, ary, index):
    elm = ctx.elements[str(index)]
    possibilty = elm.possibles[0]
    for i in range(len(ary)):
        elm2 = ctx.elements[str(ary[i])]
        p = elm2.possibles
        if possibilty in p:
            p.remove(possibilty)
            dirty_cells.append(ary[i])
            if(len(p) == 1):
                elm2.calculated = True
            elm2.update(elm2.render_numbers)

def calc_possibility_count_on_array_for_value(ctx, ary, value):
    count = 0
    index = -1
    for i in range(len(ary)):
        elm = ctx.elements[str(ary[i])]
        if len(elm.possibles) != 1:
            if value in elm.possibles:
                count += 1
                index = i
    return count, index

def check_single_possibility(ctx, ary):
    for i in range(9):
        count, index = calc_possibility_count_on_array_for_value(ctx, ary, i)
        if count == 1:
            print(f"Single possibility {i} found at {ary[index]}")
            elm = ctx.elements[str(ary[index])]
            if len(elm.possibles) != 1:
                elm.possibles = [i]
                elm.calculated = True
                elm.update(elm.render_numbers)
                dirty_cells.append(ary[index])

def get_nearby_cells(index):
    return [index * 9 + i for i in range(9)]
def get_row_cells(index):
    return [(index // 3) * 27 + (index % 3) * 3 + (i // 3) * 9 + i % 3 for i in range(9)]
def get_col_cells(index):
    return [(index // 3) * 9 + (index % 3) + (i // 3) * 27 + (i % 3) * 3 for i in range(9)]

def calc_possibilities_by_index(ctx, index):
    global dirty_cells
    index = int(index)
    if index == -1:
        return
    rows = get_row_cells((index % 9) // 3 + (index // 27) * 3)
    cols = get_col_cells(index % 3 + ((index // 9) % 3) * 3)
    nearby = get_nearby_cells(index // 9)
    
    rows.remove(index)
    cols.remove(index)
    nearby.remove(index)
    elm = ctx.elements[str(index)]
    if len(elm.possibles) == 1:
        for ary in [rows, cols, nearby]:
            remove_possibility_from_array(ctx, ary, index)
    
    if show_highlight:
        for i in range(81):
            ctx.elements[str(i)].remove_class("highlight")
        for i in range(8):
            ctx.elements[str(rows[i])].add_class("highlight")
            ctx.elements[str(cols[i])].add_class("highlight")
            ctx.elements[str(nearby[i])].add_class("highlight")
        
def on_numpad_click(ctx,id,value):
    global selected
    if value == "i":
        global show_indexes
        show_indexes = not show_indexes
        for i in range(81):
            ctx.elements[str(i)].update(ctx.elements[str(i)].render_numbers)
        return
    if value == "h":
        global show_highlight
        show_highlight = not show_highlight
        if not show_highlight:
            for i in range(81):
                ctx.elements[str(i)].remove_class("highlight")
        calc_possibilities_by_index(ctx, selected)
        return
    print(f"numpad {value} clicked")
    if selected != -1:
        elm = ctx.elements[str(selected)]
        elm.possibles = [int(value)-1]
        calc_possibilities(ctx,selected)
        elm.update(elm.render_numbers)
        
def sudoku_solver():
    global selected
    selected = -1
    with page("Sudoku Solver") as main:
        with col():
            with row().style("width: 600px; padding: 20px;align-items: end;") as numpad:
                for i in range(9):
                    button(f"{i+1}",id=f"btn-{i}").on("click",on_numpad_click)
                button("i").on("click",on_numpad_click)
                button("h").on("click",on_numpad_click)
            with grid(columns="1fr " * 3).cls("board") as board:
                for i in range(9):
                    bigcell(i)

    return main

uix.start(ui = sudoku_solver, config={"debug": True, "port": 5001, "pipes":[status_pipe()]})
