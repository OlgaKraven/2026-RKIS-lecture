import {createRoot} from 'react-dom/client';
import {LectureSite,validateCourse,validateTeacherPack} from './engine';
import './rkis.css';

const root=createRoot(document.getElementById('root')!);
async function load(){
  try{
    const base=import.meta.env.BASE_URL;
    const r=await fetch(base+'course.json',{cache:'no-store'});
    if(!r.ok)throw Error(`Не удалось получить курс: ${r.status}`);
    const course=await r.json();validateCourse(course);
    document.documentElement.style.setProperty('--rkis-font',`url("${base+course.font}")`);
    if(!['audience','print'].includes(new URLSearchParams(location.search).get('mode')||'')){
      const response=await fetch(base+'teacher-pack.json',{cache:'no-store'});
      if(!response.ok)throw Error('Не удалось получить сценарий преподавателя');
      const pack=await response.json();validateTeacherPack(pack,course);
      const key=`lecture:${base}:${course.id}:private:${course.contentVersion}`;
      try{
        const personal=JSON.parse(localStorage.getItem(key)||'{}');
        const previous=JSON.parse(localStorage.getItem(key+':author-defaults')||'{}');
        const merged:Record<string,Record<string,unknown>>={};
        for(const [id,note] of Object.entries(pack.notes as Record<string,Record<string,unknown>>)){
          merged[id]={...note};
          for(const [field,value] of Object.entries(personal[id]||{})){
            if(!Object.hasOwn(note,field))continue;
            if(!previous[id]||JSON.stringify(value)!==JSON.stringify(previous[id][field]))merged[id][field]=value;
          }
        }
        localStorage.setItem(key,JSON.stringify(merged));
        localStorage.setItem(key+':author-defaults',JSON.stringify(pack.notes));
      }catch{/* Reading the course does not depend on writable storage. */}
    }
    root.render(<LectureSite course={course} base={base}/>);
  }catch(e){root.render(<main><h1>Не удалось открыть лекции</h1><p role="alert">{String(e)}</p><button onClick={()=>void load()}>Повторить</button></main>)}
}
void load();
