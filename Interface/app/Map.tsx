'use client';
import './globals.css'
import './interface_map'
import { INCHES_PER_NODE } from './interface_map';



const PIXELS_PER_INCH = 5
const WIDTH = 800
const HEIGHT = 800
const POINT_RADIUS = PIXELS_PER_INCH * 10
const OBSTACLE_RADIUS = PIXELS_PER_INCH * Number(INCHES_PER_NODE) * 2

function realToMap(x : number,y : number,yaw : number, radius : number){
  yaw *= -1
  x *= PIXELS_PER_INCH
  y *= -PIXELS_PER_INCH

  x = (WIDTH / 2) - (radius / 2) + x
  y = (HEIGHT / 2) - (radius / 2) + y
  return [x,y,yaw]
}
var obstacles : any[][] = []

function parseMap(map_data: string){
  obstacles = []
  if (map_data == null || map_data == ""){
    console.log("No map data")
    return
  }
  var points = map_data.split('/'); //Array of Strings
  for (let i = 0; i < points.length; i++){
    if(!points[i].includes(',')){
      continue
    }
    let point = points[i].split(","); //Array of strings, x and y
    let x = Number(point[0])
    let y = Number(point[1])
    let status = String(point[2])
    let translated = realToMap(x,y,0,POINT_RADIUS);
    x = translated[0]
    y = translated[1]
    obstacles[i] = [x,y,status]
  }
  
}
function statusToColor(status: any){
  if (status == "O"){
    return 'maroon'
  }
  if (status == 'S'){
    return 'orange'
  }
  if (status == 'A'){
    return 'red'
  }
  if (status == 'T'){
    return 'green'
  }
  return 'white'
}

function obstaclesToDiv(){
    if (obstacles.length == 0){
      return
    }
    return (
    <div id="container">
      {obstacles.map((item, index) => (
        <div key={index} className="map-point" style={{
            width : String(OBSTACLE_RADIUS) + 'px',
            height : String(OBSTACLE_RADIUS) + 'px',
            left : String(item[0]) + 'px',
            top: String(item[1]) + 'px',
            backgroundColor: statusToColor(item[2]),
            borderWidth: 0
        }}/>
      ))}
    </div>
  );
    
  }

export default function Map({tx=0,ty=0,bYaw=0,tYaw=0, map_data, onMove}: any) { 
  
  var botPose = realToMap(0,0,bYaw,POINT_RADIUS)
  let bx = botPose[0]
  let by = botPose[1]
  bYaw = botPose[2]

  var tarPose = realToMap(tx,ty,tYaw,POINT_RADIUS)
  tx = tarPose[0]
  ty = tarPose[1]
  tYaw = tarPose[2]

  parseMap(map_data)

  //const [position, setPosition] = useState({ x: 0, y: 0 });
  const handleMouseDown = (event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();

    var x = event.clientX - rect.left
    var y = event.clientY - rect.top
    console.log("x: ", x, " y: ",y)
    
    x -= (WIDTH / 2)
    y -= (HEIGHT / 2)

    x -= POINT_RADIUS/2
    y -= POINT_RADIUS

    x /= PIXELS_PER_INCH
    y /= -PIXELS_PER_INCH
    console.log("translated x: ", x, " translated y: ",y)

    onMove(x, y);
  };

  return (
    
    <div>
      <h1 className='big-text' style={{
        marginTop: 100
      }}>
        MAP
      </h1>
      <div className='map-box'
      onMouseDown={handleMouseDown}
      style={{
        width : String(WIDTH) + 'px',
        height: String(HEIGHT) + 'px',
        backgroundColor: '#111',
        backgroundImage: `
          linear-gradient(to right, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
        `,
        backgroundSize: String(PIXELS_PER_INCH) + 'px '+ String(PIXELS_PER_INCH) + 'px' 
      }}>
        <div className='map-box-overlay'
        style={{
          position: 'absolute',
          
          width : '100%',
          height: '100%',
          backgroundColor: '#ff000000',
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.2) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.2) 1px, transparent 1px)
          `,
          backgroundSize: String(OBSTACLE_RADIUS) + 'px '+ String(OBSTACLE_RADIUS) + 'px' 
        }}/>
          <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(bx) + 'px',
            top: String(by) + 'px',
            backgroundColor: 'blue',
            rotate: String(bYaw) + 'rad'
        }}/>

        <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(tx) + 'px',
            top: String(ty) + 'px',
            backgroundColor: 'yellow',
            rotate: String(tYaw) + 'rad'
        }}/>
        {obstaclesToDiv()}
      </div>

    </div>
  );
}