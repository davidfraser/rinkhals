import datetime

def calc_eggday(y):
    g = y % 19
    e = 0
    c = y//100
    h = (c-c//4-(8*c+13)//25+19*g+15)%30
    i = h-(h//28)*(1-(h//28)*(29//(h+1))*((21-g)//11))
    j = (y+y//4+i+2-c+c//4)%7
    p = i-j+e
    d = 1+(p+27+(p+6)//40)%31
    m = 3+(p+26)//30
    return datetime.date(y,m,d)

def is_eggday():
    today = datetime.date.today()
    return today == calc_eggday(today.year)
