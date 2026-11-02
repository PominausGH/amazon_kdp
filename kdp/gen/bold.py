"""Bold & easy colouring objects for ages 1-4, drawn on a 400x400 canvas.
Fill slots {a}..{e} are white in the interior and coloured on the cover.
Strokes are thick and every region is big — toddlers colour with fists."""
from __future__ import annotations

L = 'fill="none"'  # line-only elements
EYE = 'fill="#000"'

OBJECTS: dict[str, str] = {
    "CAR": """
<path d="M40,300H370" {L}/>
<path d="M60,260V215Q60,198 78,194L125,188L160,142Q168,130 184,130H262Q278,130 288,142L322,188L345,195Q360,200 360,215V260Z" fill="{a}"/>
<path d="M172,148H232V186H140Z" fill="{b}"/><path d="M248,148H275L305,186H248Z" fill="{b}"/>
<circle cx="345" cy="218" r="9" fill="{c}"/>
<circle cx="120" cy="262" r="38" fill="{d}"/><circle cx="120" cy="262" r="14" fill="{e}"/>
<circle cx="300" cy="262" r="38" fill="{d}"/><circle cx="300" cy="262" r="14" fill="{e}"/>""",
    "DUMP TRUCK": """
<path d="M20,330H380" {L}/>
<path d="M40,130L235,130L245,255L40,255Z" fill="{a}"/>
<rect x="250" y="150" width="110" height="110" rx="12" fill="{b}"/>
<rect x="275" y="168" width="65" height="45" rx="6" fill="{c}"/>
<rect x="40" y="255" width="320" height="22" rx="4" fill="{e}"/>
<circle cx="100" cy="285" r="36" fill="{d}"/><circle cx="100" cy="285" r="13" fill="{e}"/>
<circle cx="300" cy="285" r="36" fill="{d}"/><circle cx="300" cy="285" r="13" fill="{e}"/>""",
    "BUS": """
<path d="M20,320H380" {L}/>
<rect x="40" y="110" width="320" height="170" rx="24" fill="{a}"/>
<rect x="62" y="135" width="58" height="58" rx="8" fill="{b}"/><rect x="134" y="135" width="58" height="58" rx="8" fill="{b}"/>
<rect x="206" y="135" width="58" height="58" rx="8" fill="{b}"/>
<rect x="282" y="135" width="56" height="120" rx="6" fill="{c}"/>
<path d="M40,220H282" {L}/>
<circle cx="110" cy="285" r="32" fill="{d}"/><circle cx="110" cy="285" r="11" fill="{e}"/>
<circle cx="290" cy="285" r="32" fill="{d}"/><circle cx="290" cy="285" r="11" fill="{e}"/>""",
    "FIRE TRUCK": """
<path d="M20,320H380" {L}/>
<rect x="40" y="170" width="230" height="100" rx="10" fill="{a}"/>
<path d="M270,270V140H330Q360,140 365,175V270Z" fill="{a}"/>
<rect x="285" y="155" width="55" height="45" rx="6" fill="{c}"/>
<rect x="300" y="116" width="26" height="24" rx="7" fill="{b}"/>
<rect x="50" y="140" width="205" height="24" rx="4" fill="{e}"/>
<path d="M80,140V164M115,140V164M150,140V164M185,140V164M220,140V164" {L}/>
<circle cx="150" cy="220" r="26" fill="{b}"/><circle cx="150" cy="220" r="9" fill="{e}"/>
<circle cx="110" cy="280" r="34" fill="{d}"/><circle cx="110" cy="280" r="12" fill="{e}"/>
<circle cx="300" cy="280" r="34" fill="{d}"/><circle cx="300" cy="280" r="12" fill="{e}"/>""",
    "TRACTOR": """
<path d="M20,345H380" {L}/>
<rect x="88" y="135" width="16" height="60" rx="4" fill="{e}"/>
<rect x="60" y="190" width="180" height="70" rx="12" fill="{a}"/>
<path d="M225,250V115H315L330,250Z" fill="{a}"/>
<rect x="245" y="132" width="58" height="50" rx="6" fill="{c}"/>
<circle cx="285" cy="275" r="68" fill="{d}"/><circle cx="285" cy="275" r="26" fill="{b}"/>
<circle cx="105" cy="300" r="42" fill="{d}"/><circle cx="105" cy="300" r="15" fill="{b}"/>""",
    "ROCKET": """
<path d="M200,40C250,90 262,160 255,280H145C138,160 150,90 200,40Z" fill="{a}"/>
<circle cx="200" cy="150" r="30" fill="{c}"/>
<path d="M146,205L95,290L145,280Z" fill="{b}"/><path d="M254,205L305,290L255,280Z" fill="{b}"/>
<path d="M165,280H235L225,305H175Z" fill="{e}"/>
<path d="M178,305Q200,375 222,305Z" fill="{d}"/>
<path d="M60,70l8,16l16,8l-16,8l-8,16l-8-16l-16-8l16-8z" fill="{d}"/><path d="M335,120l6,12l12,6l-12,6l-6,12l-6-12l-12-6l12-6z" fill="{d}"/>""",
    "SAILBOAT": """
<path d="M200,48V270" {L}/>
<path d="M205,62V250H322Z" fill="{a}"/><path d="M195,92V250H92Z" fill="{b}"/>
<path d="M200,48L238,62L200,76Z" fill="{d}"/>
<path d="M58,270H342L302,330H98Z" fill="{c}"/>
<path d="M10,350Q50,328 90,350T170,350T250,350T330,350T410,350" {L}/>""",
    "AIRPLANE": """
<path d="M180,170H222L196,88H164Z" fill="{b}"/>
<path d="M70,176L58,108H100L125,172Z" fill="{c}"/>
<path d="M50,200Q50,170 90,170H320Q370,175 370,200Q370,225 320,230H90Q50,230 50,200Z" fill="{a}"/>
<path d="M320,175Q352,180 362,198H320Z" fill="{e}"/>
<circle cx="150" cy="198" r="11" fill="{e}"/><circle cx="195" cy="198" r="11" fill="{e}"/><circle cx="240" cy="198" r="11" fill="{e}"/><circle cx="285" cy="198" r="11" fill="{e}"/>
<path d="M170,210H232L192,322H150Z" fill="{b}"/>
<path d="M40,330Q60,305 85,320Q100,300 120,320Q140,318 140,335Z" fill="{d}"/>""",
    "TRAIN": """
<path d="M10,338H390" {L}/>
<path d="M88,170L82,110H138L132,170Z" fill="{e}"/>
<rect x="60" y="170" width="175" height="110" rx="20" fill="{a}"/>
<rect x="230" y="110" width="120" height="175" rx="8" fill="{b}"/>
<rect x="218" y="94" width="144" height="22" rx="6" fill="{e}"/>
<rect x="255" y="135" width="70" height="55" rx="6" fill="{c}"/>
<path d="M60,280L28,320H82Z" fill="{e}"/>
<circle cx="105" cy="305" r="28" fill="{d}"/><circle cx="180" cy="305" r="28" fill="{d}"/><circle cx="290" cy="298" r="38" fill="{d}"/>
<circle cx="112" cy="70" r="18" fill="{e}"/><circle cx="145" cy="45" r="13" fill="{e}"/>""",
    "HELICOPTER": """
<path d="M130,185L40,175V205L130,225Z" fill="{a}"/>
<ellipse cx="38" cy="172" rx="10" ry="34" fill="{c}"/>
<ellipse cx="230" cy="210" rx="105" ry="70" fill="{a}"/>
<path d="M235,145Q318,150 330,205H235Z" fill="{c}"/>
<rect x="222" y="117" width="16" height="25" fill="{e}"/>
<rect x="105" y="104" width="250" height="14" rx="7" fill="{b}"/>
<path d="M170,270L155,295M290,270L305,295" {L}/>
<rect x="120" y="292" width="215" height="12" rx="6" fill="{e}"/>""",
    "HOT AIR BALLOON": """
<path d="M200,40C300,40 332,120 300,190C285,225 245,250 235,265H165C155,250 115,225 100,190C68,120 100,40 200,40Z" fill="{a}"/>
<path d="M200,40C160,80 152,190 172,265H228C248,190 240,80 200,40Z" fill="{b}"/>
<path d="M170,265L176,295M230,265L224,295" {L}/>
<rect x="168" y="295" width="64" height="50" rx="6" fill="{c}"/>
<path d="M30,110Q30,85 55,88Q65,65 90,75Q112,80 108,105Q118,125 95,128H45Q28,126 30,110Z" fill="{d}"/>""",
    "SUBMARINE": """
<rect x="150" y="130" width="90" height="60" rx="10" fill="{b}"/>
<path d="M215,130V85H252" {L} stroke-width="12"/>
<rect x="50" y="180" width="300" height="110" rx="55" fill="{a}"/>
<circle cx="130" cy="235" r="19" fill="{c}"/><circle cx="200" cy="235" r="19" fill="{c}"/><circle cx="270" cy="235" r="19" fill="{c}"/>
<ellipse cx="38" cy="235" rx="11" ry="32" fill="{d}"/>
<circle cx="360" cy="150" r="10" fill="{e}"/><circle cx="374" cy="118" r="7" fill="{e}"/><circle cx="352" cy="92" r="12" fill="{e}"/>""",
    "DIGGER": """
<path d="M20,345H380" {L}/>
<rect x="60" y="265" width="200" height="55" rx="27" fill="{e}"/>
<circle cx="90" cy="292" r="16" fill="{d}"/><circle cx="160" cy="292" r="16" fill="{d}"/><circle cx="230" cy="292" r="16" fill="{d}"/>
<rect x="80" y="180" width="170" height="85" rx="8" fill="{a}"/>
<rect x="170" y="110" width="80" height="75" rx="8" fill="{a}"/>
<rect x="185" y="125" width="50" height="40" rx="4" fill="{c}"/>
<path d="M245,200L318,108L340,124L268,216Z" fill="{b}"/>
<path d="M318,108L362,190L342,201L304,126Z" fill="{b}"/>
<path d="M338,190L386,198L376,252Q348,258 332,235Z" fill="{e}"/>""",
    "BICYCLE": """
<circle cx="110" cy="260" r="65" fill="{a}"/><circle cx="110" cy="260" r="45" fill="{e}"/>
<circle cx="300" cy="260" r="65" fill="{a}"/><circle cx="300" cy="260" r="45" fill="{e}"/>
<path d="M110,260L170,170H270L300,260M170,170L200,260L270,170M110,260H200" {L} stroke-width="10"/>
<path d="M145,152H198Q198,170 176,170H160Z" fill="{b}"/>
<path d="M262,170L250,132L290,126" {L} stroke-width="10"/>""",
    "SUN": """
<g fill="{b}">""" + "".join(
        f'<path d="M200,40L216,92H184Z" transform="rotate({k*30} 200 200)"/>' for k in range(12)) + """</g>
<circle cx="200" cy="200" r="95" fill="{a}"/>
<circle cx="168" cy="180" r="10" {EYE}/><circle cx="232" cy="180" r="10" {EYE}/>
<path d="M155,225Q200,265 245,225" {L}/>""",
    "HOUSE": """
<path d="M10,340H390" {L}/>
<rect x="255" y="95" width="32" height="70" fill="{e}"/>
<rect x="90" y="190" width="220" height="150" fill="{a}"/>
<path d="M68,198L200,80L332,198Z" fill="{b}"/>
<rect x="175" y="262" width="50" height="78" rx="4" fill="{c}"/><circle cx="214" cy="302" r="5" {EYE}/>
<rect x="110" y="214" width="50" height="46" fill="{d}"/><path d="M135,214V260M110,237H160" {L}/>
<rect x="240" y="214" width="50" height="46" fill="{d}"/><path d="M265,214V260M240,237H290" {L}/>""",
    "TREE": """
<path d="M20,345H380" {L}/>
<path d="M178,345L186,230H214L222,345Z" fill="{b}"/>
<path d="M110,250Q60,240 78,185Q70,120 140,118Q160,58 230,72Q300,80 300,140Q345,170 320,222Q312,256 270,250Z" fill="{a}"/>
<circle cx="150" cy="170" r="14" fill="{c}"/><circle cx="240" cy="140" r="14" fill="{c}"/><circle cx="265" cy="210" r="14" fill="{c}"/><circle cx="175" cy="225" r="14" fill="{c}"/>""",
    "APPLE": """
<path d="M200,120C140,80 70,120 80,200C90,280 150,330 200,310C250,330 310,280 320,200C330,120 260,80 200,120Z" fill="{a}"/>
<path d="M200,120Q195,90 212,66" {L} stroke-width="10"/>
<path d="M207,96Q240,58 278,80Q242,112 207,96Z" fill="{b}"/>
<path d="M120,170Q125,140 150,132" {L}/>""",
    "ICE CREAM": """
<path d="M140,205H260L200,352Z" fill="{b}"/>
<path d="M160,250L230,215M175,290L248,232M152,232L215,205M186,325L237,262" {L}/>
<path d="M132,208Q112,150 160,128Q200,62 242,124Q290,145 268,208Z" fill="{a}"/>
<path d="M150,170Q170,180 165,200M245,165Q232,185 240,200" {L}/>
<circle cx="203" cy="80" r="15" fill="{c}"/>""",
    "CUPCAKE": """
<path d="M120,220H280L260,340H140Z" fill="{b}"/>
<path d="M160,222L168,340M200,222V340M240,222L232,340" {L}/>
<path d="M104,226Q94,180 140,175Q140,120 200,115Q260,120 260,175Q306,180 296,226Z" fill="{a}"/>
<circle cx="200" cy="98" r="19" fill="{c}"/>
<path d="M150,160l10,8M235,150l8,10M195,180l-4,12M245,200l10,-4M160,205l-8,6" {L} stroke-width="7"/>""",
    "FISH": """
<path d="M288,200L352,145L340,200L352,255Z" fill="{b}"/>
<path d="M75,200Q180,95 292,200Q180,305 75,200Z" fill="{a}"/>
<path d="M170,152Q200,108 240,150Z" fill="{b}"/>
<circle cx="130" cy="188" r="15" fill="#fff"/><circle cx="133" cy="188" r="7" {EYE}/>
<path d="M200,160Q225,200 200,240" {L}/>
<circle cx="60" cy="120" r="12" fill="{c}"/><circle cx="85" cy="85" r="8" fill="{c}"/>""",
    "UMBRELLA": """
<path d="M200,200V318Q200,345 175,345Q152,345 152,322" {L} stroke-width="11"/>
<path d="M60,200Q60,92 200,80Q340,92 340,200Q305,180 270,200Q235,180 200,200Q165,180 130,200Q95,180 60,200Z" fill="{a}"/>
<path d="M200,80Q165,130 130,200M200,80Q235,130 270,200" {L}/>
<path d="M200,80V200" {L}/>
<path d="M200,80V60" {L} stroke-width="10"/>""",
    "BALLOONS": """
<path d="M140,205Q160,280 200,360M260,195Q240,280 200,360M200,270V360" {L} stroke-width="5"/>
<ellipse cx="140" cy="140" rx="52" ry="64" fill="{a}"/><path d="M134,204L146,204L140,212Z" fill="{a}"/>
<ellipse cx="262" cy="130" rx="52" ry="64" fill="{b}"/><path d="M256,194L268,194L262,202Z" fill="{b}"/>
<ellipse cx="200" cy="205" rx="48" ry="60" fill="{c}"/><path d="M194,265L206,265L200,273Z" fill="{c}"/>""",
    "FLOWER": """
<path d="M200,215Q188,290 200,355" {L} stroke-width="10"/>
<path d="M195,300Q140,260 120,290Q150,320 195,300Z" fill="{b}"/><path d="M203,275Q260,240 280,268Q250,300 203,275Z" fill="{b}"/>
<g fill="{a}">""" + "".join(
        f'<ellipse cx="200" cy="88" rx="34" ry="48" transform="rotate({k*60} 200 150)"/>' for k in range(6)) + """</g>
<circle cx="200" cy="150" r="38" fill="{c}"/>""",
    "BUTTERFLY": """
<path d="M196,190C150,80 40,70 60,150C70,200 140,205 196,200Z" fill="{a}"/>
<path d="M204,190C250,80 360,70 340,150C330,200 260,205 204,200Z" fill="{a}"/>
<path d="M196,205C120,210 90,290 140,305C175,312 192,260 196,215Z" fill="{b}"/>
<path d="M204,205C280,210 310,290 260,305C225,312 208,260 204,215Z" fill="{b}"/>
<circle cx="120" cy="140" r="20" fill="{c}"/><circle cx="280" cy="140" r="20" fill="{c}"/>
<ellipse cx="200" cy="200" rx="13" ry="78" fill="{d}"/>
<path d="M195,128Q180,90 160,78M205,128Q220,90 240,78" {L} stroke-width="6"/>""",
    "SNAIL": """
<path d="M20,330H380" {L}/>
<path d="M60,318H312Q342,318 342,290L336,198Q333,175 312,178Q296,182 296,205L298,262H90Q60,262 60,290Z" fill="{b}"/>
<path d="M312,180L298,130M330,184L344,136" {L} stroke-width="6"/>
<circle cx="296" cy="124" r="10" {EYE}/><circle cx="346" cy="130" r="10" {EYE}/>
<circle cx="180" cy="200" r="85" fill="{a}"/>
<path d="M180,200m0,-12a12,12 0 1 1 -12,12a28,28 0 0 1 28,-28a44,44 0 0 1 44,44a62,62 0 0 1 -62,62a78,78 0 0 1 -78,-78" {L}/>""",
    "KITE": """
<path d="M200,300Q170,330 200,355Q232,378 205,398" {L} stroke-width="5"/>
<path d="M200,40L292,160L200,300L108,160Z" fill="{a}"/>
<path d="M200,40V300M108,160H292" {L}/>
<path d="M180,330L160,318L162,342Z" fill="{b}"/><path d="M220,350L240,338L238,362Z" fill="{b}"/>""",
    "STAR": """
<path d="M200,45L242,150L355,155L268,225L298,335L200,272L102,335L132,225L45,155L158,150Z" fill="{a}"/>
<circle cx="175" cy="190" r="9" {EYE}/><circle cx="225" cy="190" r="9" {EYE}/>
<path d="M170,225Q200,252 230,225" {L}/>
<circle cx="150" cy="215" r="10" fill="{b}"/><circle cx="250" cy="215" r="10" fill="{b}"/>""",
}

OBJECTS["DELIVERY TRUCK"] = OBJECTS.pop("DUMP TRUCK")

_WHEELS = """<circle cx="{x1}" cy="{y}" r="{r}" fill="{{d}}"/><circle cx="{x1}" cy="{y}" r="{h}" fill="{{e}}"/>
<circle cx="{x2}" cy="{y}" r="{r}" fill="{{d}}"/><circle cx="{x2}" cy="{y}" r="{h}" fill="{{e}}"/>"""


def _wheels(x1, x2, y, r=34, h=12):
    return _WHEELS.format(x1=x1, x2=x2, y=y, r=r, h=h).replace("{{", "{").replace("}}", "}")


OBJECTS.update({
    "DUMP TRUCK": """
<path d="M20,330H380" {L}/>
<path d="M30,95L215,140L205,250L50,250Z" fill="{a}"/>
<path d="M58,150L190,182M62,200L186,215" {L}/>
<rect x="240" y="150" width="120" height="110" rx="12" fill="{b}"/>
<rect x="268" y="168" width="70" height="45" rx="6" fill="{c}"/>
<rect x="40" y="250" width="320" height="22" rx="4" fill="{e}"/>""" + _wheels(105, 300, 285, 36, 13),
    "GARBAGE TRUCK": """
<path d="M20,330H380" {L}/>
<path d="M40,262V140Q40,110 70,110H240V262Z" fill="{a}"/>
<path d="M70,140V230M110,140V230M150,140V230M190,140V230" {L}/>
<path d="M240,262V150H320Q345,150 355,180L362,262Z" fill="{b}"/>
<rect x="262" y="168" width="58" height="45" rx="6" fill="{c}"/>
<rect x="20" y="200" width="24" height="60" rx="4" fill="{e}"/>""" + _wheels(110, 305, 280),
    "CEMENT MIXER": """
<path d="M20,330H380" {L}/>
<rect x="40" y="245" width="320" height="22" rx="4" fill="{e}"/>
<ellipse cx="140" cy="175" rx="105" ry="70" transform="rotate(-12 140 175)" fill="{a}"/>
<path d="M70,135Q110,200 95,235M130,110Q170,180 155,240M190,110Q225,170 215,225" {L}/>
<rect x="255" y="135" width="105" height="115" rx="12" fill="{b}"/>
<rect x="280" y="152" width="58" height="45" rx="6" fill="{c}"/>""" + _wheels(105, 300, 280),
    "POLICE CAR": """
<path d="M40,300H370" {L}/>
<rect x="180" y="102" width="56" height="28" rx="8" fill="{b}"/>
<path d="M60,260V215Q60,198 78,194L125,188L160,142Q168,130 184,130H262Q278,130 288,142L322,188L345,195Q360,200 360,215V260Z" fill="{a}"/>
<path d="M172,148H232V186H140Z" fill="{c}"/><path d="M248,148H275L305,186H248Z" fill="{c}"/>
<rect x="150" y="205" width="110" height="34" rx="8" fill="{e}"/>""" + _wheels(120, 300, 262, 38, 14),
    "AMBULANCE": """
<path d="M20,320H380" {L}/>
<rect x="40" y="110" width="220" height="170" rx="14" fill="{a}"/>
<path d="M135,150H165V180H195V210H165V240H135V210H105V180H135Z" fill="{b}"/>
<path d="M260,280V160H320Q345,160 355,190L362,280Z" fill="{a}"/>
<rect x="275" y="175" width="52" height="42" rx="6" fill="{c}"/>
<rect x="120" y="88" width="50" height="24" rx="8" fill="{b}"/>""" + _wheels(110, 300, 285, 32, 11),
    "MOTORBIKE": """
<path d="M20,330H380" {L}/>
<circle cx="95" cy="270" r="58" fill="{d}"/><circle cx="95" cy="270" r="20" fill="{e}"/>
<circle cx="305" cy="270" r="58" fill="{d}"/><circle cx="305" cy="270" r="20" fill="{e}"/>
<path d="M95,270L150,205H255L305,270" {L} stroke-width="10"/>
<path d="M140,210Q150,165 210,165H250L265,210Z" fill="{a}"/>
<path d="M118,175H190Q190,195 160,195H128Z" fill="{b}"/>
<path d="M262,205L282,128L315,120" {L} stroke-width="10"/>
<circle cx="300" cy="160" r="14" fill="{c}"/>""",
    "CRANE": """
<path d="M10,345H390" {L}/>
<rect x="110" y="70" width="40" height="215" fill="{a}"/>
<path d="M110,100L150,130M150,100L110,130M110,150L150,180M150,150L110,180M110,200L150,230M150,200L110,230" {L} stroke-width="5"/>
<path d="M60,58H380V82H60Z" fill="{a}"/>
<rect x="40" y="56" width="45" height="38" rx="4" fill="{e}"/>
<path d="M330,82V200" {L} stroke-width="5"/>
<rect x="300" y="200" width="60" height="45" rx="4" fill="{c}"/>
<rect x="60" y="285" width="160" height="40" rx="8" fill="{b}"/>""" + _wheels(85, 195, 330, 18, 6),
})

_STAR_TOP ='M200,8L210,32L235,33L216,48L223,72L200,58L177,72L184,48L165,33L190,32Z'

OBJECTS.update({
    "SNOWMAN": """
<circle cx="200" cy="292" r="80" fill="{a}"/><circle cx="200" cy="185" r="58" fill="{a}"/>
<circle cx="200" cy="102" r="44" fill="{a}"/>
<rect x="168" y="20" width="64" height="46" rx="4" fill="{e}"/><rect x="150" y="60" width="100" height="12" rx="6" fill="{e}"/>
<circle cx="184" cy="95" r="6" {EYE}/><circle cx="216" cy="95" r="6" {EYE}/>
<path d="M200,108L246,116L200,122Z" fill="{d}"/>
<path d="M150,140Q200,160 250,140L252,160Q200,180 148,160Z" fill="{b}"/><path d="M228,160L240,215L215,215L210,165Z" fill="{b}"/>
<circle cx="200" cy="200" r="7" {EYE}/><circle cx="200" cy="228" r="7" {EYE}/><circle cx="200" cy="275" r="8" {EYE}/>""",
    "CHRISTMAS TREE": """
<rect x="178" y="325" width="44" height="45" rx="4" fill="{e}"/>
<path d="M200,45L285,150H245L318,240H268L352,330H48L132,240H82L155,150H115Z" fill="{a}"/>
<circle cx="190" cy="120" r="12" fill="{b}"/><circle cx="150" cy="200" r="13" fill="{c}"/><circle cx="250" cy="195" r="13" fill="{d}"/>
<circle cx="200" cy="250" r="13" fill="{b}"/><circle cx="120" cy="300" r="13" fill="{d}"/><circle cx="280" cy="295" r="13" fill="{c}"/>
<path d="M150,160Q200,185 250,160M118,250Q200,282 282,250" {L}/>
<path d="__STAR__" fill="{b}"/>""".replace("__STAR__", _STAR_TOP),
    "PRESENT": """
<path d="M200,128C150,62 105,108 200,128ZM200,128C250,62 295,108 200,128Z" fill="{b}"/>
<rect x="80" y="172" width="240" height="180" rx="6" fill="{a}"/>
<rect x="65" y="128" width="270" height="52" rx="8" fill="{a}"/>
<rect x="180" y="128" width="40" height="224" fill="{b}"/>""",
    "STOCKING": """
<path d="M150,95H270V230Q270,250 255,265L190,330Q160,360 125,335Q95,305 125,275L150,250Z" fill="{a}"/>
<path d="M140,300Q125,320 140,335Q160,350 178,333L160,310Z" fill="{c}"/>
<rect x="132" y="50" width="156" height="58" rx="14" fill="{e}"/>
<path d="M285,70Q320,60 318,90" {L}/>""",
    "CANDY CANE": """
<path d="M240,355V160A58,58 0 0 0 124,160V185" {L} stroke-width="60"/>
<path d="M240,355V160A58,58 0 0 0 124,160V185" fill="none" stroke="{a}" stroke-width="44"/>
<path d="M218,330L262,310M218,280L262,260M218,230L262,210M218,180L262,160M200,120L230,92M156,106L172,140M102,165H146" {L} stroke-width="6"/>
<path d="M240,250C200,215 170,250 240,262ZM240,250C280,215 310,250 240,262Z" fill="{b}"/>""",
    "GINGERBREAD": """
<path d="M150,150H250L330,180Q350,195 335,215L262,205L276,330Q278,355 250,352L200,300L150,352Q122,355 124,330L138,205L65,215Q50,195 70,180Z" fill="{a}"/>
<circle cx="200" cy="98" r="54" fill="{a}"/>
<circle cx="182" cy="88" r="7" {EYE}/><circle cx="218" cy="88" r="7" {EYE}/>
<path d="M178,115Q200,135 222,115" {L}/>
<circle cx="200" cy="190" r="10" fill="{b}"/><circle cx="200" cy="230" r="10" fill="{c}"/><circle cx="200" cy="270" r="10" fill="{b}"/>
<path d="M80,190l10,12l10,-12l10,12M290,190l10,12l10,-12l10,12M140,325l10,10l10,-10M240,325l10,10l10,-10" {L} stroke-width="5"/>""",
    "BELL": """
<circle cx="200" cy="58" r="16" fill="{e}"/><circle cx="200" cy="300" r="24" fill="{e}"/>
<path d="M200,70C140,70 120,130 120,200C120,250 95,270 80,290H320C305,270 280,250 280,200C280,130 260,70 200,70Z" fill="{a}"/>
<path d="M128,240Q200,262 272,240" {L}/>
<path d="M200,78C150,30 110,70 200,82ZM200,78C250,30 290,70 200,82Z" fill="{b}"/>""",
    "BAUBLE": """
<path d="M200,82Q200,40 232,45" {L} stroke-width="6"/>
<circle cx="200" cy="222" r="120" fill="{a}"/>
<path d="M87,182Q200,217 313,182M87,262Q200,297 313,262" {L}/>
<circle cx="140" cy="222" r="12" fill="{b}"/><circle cx="200" cy="230" r="12" fill="{c}"/><circle cx="260" cy="222" r="12" fill="{b}"/>
<rect x="170" y="82" width="60" height="32" rx="5" fill="{e}"/>""",
    "SNOWFLAKE": """<g fill="{a}">""" + "".join(
        f'<path d="M200,200L218,135L200,40L182,135Z" transform="rotate({k*60} 200 200)"/>'
        f'<path d="M200,105L232,82L232,118Z" transform="rotate({k*60} 200 200)"/>'
        f'<path d="M200,105L168,82L168,118Z" transform="rotate({k*60} 200 200)"/>' for k in range(6)) + """</g>
<circle cx="200" cy="200" r="34" fill="{b}"/>""",
    "MITTEN": """
<path d="M140,330V170Q140,90 210,90Q280,90 280,170V190L305,160Q330,140 345,165Q352,180 330,210L280,280V330Z" fill="{a}"/>
<path d="M175,170l12,14l12,-14l12,14l12,-14l12,14M175,220l12,14l12,-14l12,14l12,-14l12,14" {L} stroke-width="5"/>
<rect x="124" y="310" width="172" height="56" rx="12" fill="{b}"/>""",
    "REINDEER": """
<path d="M165,150L130,70M148,110L100,100M138,90L150,45M235,150L270,70M252,110L300,100M262,90L250,45" {L} stroke-width="14"/>
<ellipse cx="118" cy="170" rx="38" ry="18" transform="rotate(-25 118 170)" fill="{b}"/>
<ellipse cx="282" cy="170" rx="38" ry="18" transform="rotate(25 282 170)" fill="{b}"/>
<ellipse cx="200" cy="235" rx="82" ry="102" fill="{b}"/>
<ellipse cx="200" cy="290" rx="55" ry="42" fill="{e}"/>
<circle cx="170" cy="210" r="9" {EYE}/><circle cx="230" cy="210" r="9" {EYE}/>
<circle cx="200" cy="278" r="26" fill="{a}"/>""",
    "SLEIGH": """
<rect x="110" y="140" width="70" height="70" rx="4" fill="{c}"/><rect x="170" y="165" width="60" height="45" rx="4" fill="{d}"/>
<path d="M70,300V205Q70,182 92,192L122,215H262L300,150Q322,128 332,160L312,300Z" fill="{a}"/>
<path d="M110,300V330M290,300V330" {L} stroke-width="10"/>
<path d="M40,330H335Q372,330 372,295" {L} stroke-width="12"/>""",
    "WREATH": """
<circle cx="200" cy="190" r="140" fill="{a}"/><circle cx="200" cy="190" r="75" fill="#fff"/>
<path d="M95,120l20,10M300,120l-20,10M80,215l22,-4M320,215l-22,-4M150,80l10,18M250,80l-10,18" {L}/>
<circle cx="120" cy="160" r="12" fill="{c}"/><circle cx="280" cy="160" r="12" fill="{c}"/><circle cx="200" cy="75" r="12" fill="{c}"/>
<path d="M195,325L170,380H195L205,330ZM205,325L230,380H205Z" fill="{b}"/>
<path d="M200,315C140,265 125,345 200,325ZM200,315C260,265 275,345 200,325Z" fill="{b}"/>""",
    "HOT COCOA": """
<circle cx="292" cy="245" r="52" fill="{a}"/><circle cx="292" cy="245" r="28" fill="#fff"/>
<rect x="110" y="150" width="175" height="195" rx="22" fill="{a}"/>
<rect x="130" y="132" width="40" height="34" rx="8" fill="{e}"/><rect x="180" y="125" width="40" height="40" rx="8" fill="{e}"/><rect x="228" y="134" width="38" height="32" rx="8" fill="{e}"/>
<path d="M160,110Q140,85 160,60Q180,35 160,15M240,110Q220,85 240,60" {L} stroke-width="6"/>
<path d="M160,250l20,-25l20,25l20,-25l20,25" {L}/>""",
    "PENGUIN": """
<ellipse cx="160" cy="355" rx="34" ry="14" fill="{d}"/><ellipse cx="240" cy="355" rx="34" ry="14" fill="{d}"/>
<path d="M95,190Q60,250 85,300Q110,260 110,215Z" fill="{e}"/><path d="M305,190Q340,250 315,300Q290,260 290,215Z" fill="{e}"/>
<ellipse cx="200" cy="215" rx="110" ry="142" fill="{e}"/>
<path d="M200,95C130,95 125,165 130,200C135,300 170,345 200,345C230,345 265,300 270,200C275,165 270,95 200,95Z" fill="{b}"/>
<circle cx="178" cy="140" r="9" {EYE}/><circle cx="222" cy="140" r="9" {EYE}/>
<path d="M180,160H220L200,185Z" fill="{d}"/>""",
    "HOLLY": """
<path d="M200,210C140,150 70,170 55,200C80,195 90,215 75,230C110,220 120,245 110,260C150,250 190,245 200,210Z" fill="{a}"/>
<path d="M200,210C260,150 330,170 345,200C320,195 310,215 325,230C290,220 280,245 290,260C250,250 210,245 200,210Z" fill="{a}"/>
<path d="M200,210C150,240 140,310 170,340C175,315 195,315 200,330C205,315 225,315 230,340C260,310 250,240 200,210Z" fill="{a}"/>
<circle cx="180" cy="180" r="24" fill="{c}"/><circle cx="222" cy="176" r="24" fill="{c}"/><circle cx="200" cy="145" r="24" fill="{c}"/>""",
    "SANTA HAT": """
<path d="M85,285C110,140 230,70 318,108C350,124 346,190 332,212C302,162 252,152 222,192C204,222 300,250 318,285Z" fill="{a}"/>
<circle cx="332" cy="226" r="32" fill="{e}"/>
<rect x="60" y="268" width="285" height="64" rx="32" fill="{e}"/>""",
    "SNOW GLOBE": """
<circle cx="200" cy="175" r="132" fill="{c}"/>
<path d="M200,95L245,170H222L262,235H138L178,170H155Z" fill="{a}"/>
<path d="M90,232Q200,262 310,232" {L}/>
<circle cx="120" cy="110" r="7" fill="{e}"/><circle cx="285" cy="130" r="7" fill="{e}"/><circle cx="150" cy="70" r="6" fill="{e}"/><circle cx="260" cy="80" r="6" fill="{e}"/>
<path d="M100,290H300L322,360H78Z" fill="{b}"/>""",
    "IGLOO": """
<path d="M20,320H380" {L}/>
<path d="M60,320A140,140 0 0 1 340,320Z" fill="{a}"/>
<path d="M70,270H330M95,225H305M135,190H265M120,320V270M200,270V225M280,320V270M160,225V190M240,225V190" {L}/>
<path d="M160,320V280A40,40 0 0 1 240,280V320Z" fill="{e}"/>""",
    "CANDLE": """
<rect x="165" y="150" width="70" height="190" rx="6" fill="{a}"/>
<path d="M200,145V125" {L} stroke-width="6"/>
<path d="M200,40Q245,95 200,125Q155,95 200,40Z" fill="{b}"/>
<path d="M200,345C140,320 85,330 70,355C110,350 120,375 110,385C150,375 190,375 200,345Z" fill="{d}"/>
<path d="M200,345C260,320 315,330 330,355C290,350 280,375 290,385C250,375 210,375 200,345Z" fill="{d}"/>
<circle cx="200" cy="350" r="16" fill="{c}"/>""",
})

THEMES = {
    "vehicles": ["DUMP TRUCK", "DIGGER", "GARBAGE TRUCK", "FIRE TRUCK", "CEMENT MIXER", "TRACTOR", "CRANE",
                 "POLICE CAR", "AMBULANCE", "CAR", "DELIVERY TRUCK", "BUS", "TRAIN", "MOTORBIKE", "BICYCLE",
                 "ROCKET", "AIRPLANE", "HELICOPTER", "HOT AIR BALLOON", "SAILBOAT", "SUBMARINE"],
    "everyday": ["SUN", "HOUSE", "TREE", "APPLE", "ICE CREAM", "CUPCAKE", "FISH", "UMBRELLA",
                 "BALLOONS", "FLOWER", "BUTTERFLY", "SNAIL", "KITE", "STAR"],
    "christmas": ["CHRISTMAS TREE", "SNOWMAN", "PRESENT", "STOCKING", "CANDY CANE", "GINGERBREAD", "BELL",
                  "BAUBLE", "SNOWFLAKE", "MITTEN", "REINDEER", "SLEIGH", "WREATH", "HOT COCOA", "PENGUIN",
                  "HOLLY", "SANTA HAT", "SNOW GLOBE", "IGLOO", "CANDLE", "STAR"],
}

PALETTES = [
    dict(a="#ff6b6b", b="#ffd93d", c="#6bcBef", d="#55c271", e="#9b8cff"),
    dict(a="#4d96ff", b="#ffd93d", c="#ff8fab", d="#6bcB77", e="#ffa45b"),
    dict(a="#ffa45b", b="#4d96ff", c="#ffd93d", d="#ff6b6b", e="#7bdff2"),
]


def draw(name: str, stroke=8.0, palette: dict | None = None) -> str:
    body = OBJECTS[name].replace("{L}", L).replace("{EYE}", EYE)
    cols = palette or dict(a="#fff", b="#fff", c="#fff", d="#fff", e="#fff")
    for k, v in cols.items():
        body = body.replace("{" + k + "}", v)
    return (f'<g stroke="#000" stroke-width="{stroke}" stroke-linejoin="round" '
            f'stroke-linecap="round">{body}</g>')
