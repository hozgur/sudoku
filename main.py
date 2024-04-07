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
    color: #00d;
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
class cell(uix.Element):
    selected = -1
    def __init__(self, id, value=None):
        super().__init__(id = str(id), value = value)
        self.possibles = pv.copy()
        self.calculated = False
        with self.on("click",self.on_click).cls("cell selected" if cell.selected == self.id else "cell"):
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
        print(f"cell {self.id} clicked") 
        for i in range(9):
            if i in self.possibles:
                print(f"btn-{i} enabled")
                ctx.elements[f"btn-{i}"].set_attr("disabled",False)
            else:
                ctx.elements[f"btn-{i}"].set_attr("disabled",True)      
        calc_possibilities(ctx, self.id)

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


def calc_possibilities_by_index(ctx, index):
    global dirty_cells
    index = int(index)
    if index == -1:
        return
    big_index = index // 9
    row_index = (index % 9) // 3 + (big_index // 3) * 3
    col_index = index % 3 + (big_index % 3) * 3
    rows = []
    cols = []
    nearby = []
    for i in range(9):
        rows.append((row_index // 3) *27 + (row_index % 3) * 3 + (i // 3) * 9 + i % 3) 
    for i in range(9):
        cols.append((col_index // 3) * 9 + (col_index % 3) + (i // 3) * 27 + (i % 3) * 3)
    for i in range(9):
        nearby.append(big_index * 9 + i)

    rows.remove(index)
    cols.remove(index)
    nearby.remove(index)
    dirty_count = len(dirty_cells)
    elm = ctx.elements[str(index)]
    if len(elm.possibles) == 1:
        val = elm.possibles[0]
        for i in range(len(rows)):
            p = ctx.elements[str(rows[i])].possibles
            if val in p:
                print(f"removing {val} from {rows[i]}")
                p.remove(val)
                if(len(p) == 1):
                    dirty_cells.append(rows[i])
                    ctx.elements[str(rows[i])].calculated = True
                    
        for i in range(len(cols)):
            p = ctx.elements[str(cols[i])].possibles
            if val in p:
                p.remove(val)
                if(len(p) == 1):
                    dirty_cells.append(cols[i])
                    ctx.elements[str(cols[i])].calculated = True
        for i in range(len(nearby)):
            p = ctx.elements[str(nearby[i])].possibles
            if val in p:
                p.remove(val)
                if(len(p) == 1):
                    dirty_cells.append(nearby[i])
                    ctx.elements[str(nearby[i])].calculated = True

    

    for i in range(81):
        ctx.elements[str(i)].update(ctx.elements[str(i)].render_numbers)

    if cell.selected != -1:
        ctx.elements[str(cell.selected)].remove_class("selected")
    cell.selected = str(index)
    ctx.elements[str(cell.selected)].add_class("selected")

    if show_highlight:
        for i in range(81):
            ctx.elements[str(i)].remove_class("highlight")
        for i in range(8):
            ctx.elements[str(rows[i])].add_class("highlight")
            ctx.elements[str(cols[i])].add_class("highlight")
            ctx.elements[str(nearby[i])].add_class("highlight")
        
def on_numpad_click(ctx,id,value):
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
        calc_possibilities_by_index(ctx, cell.selected)
        return
    print(f"numpad {value} clicked")
    if cell.selected != -1:
        elm = ctx.elements[str(cell.selected)]
        elm.possibles = [int(value)-1]
        elm.update(elm.render_numbers)
        calc_possibilities(ctx,cell.selected)
        
def sudoku_solver():
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
