import fs from 'node:fs';
import assert from 'node:assert/strict';
import {validateCourse} from '../src/engine/model.ts';
import {validateTeacherPack,courseAssets} from '../src/engine/validation.ts';
const course=JSON.parse(fs.readFileSync('public/course.json','utf8'));
const pack=JSON.parse(fs.readFileSync('public/teacher-pack.json','utf8'));
const explanations=JSON.parse(fs.readFileSync('public/explanations.json','utf8'));
validateCourse(course);validateTeacherPack(pack,course);
assert.equal(course.lectures.length,31);
for(const [semester,count] of [[5,19],[6,7],[7,5]])assert.equal(course.lectures.filter(l=>l.semester===semester).length,count);
for(const asset of courseAssets(course))if(!/^https?:/.test(asset))assert.ok(fs.existsSync('public/'+asset),asset);
for(const l of course.lectures){
  assert.equal(l.slides[0].kind,'title');
  for(const s of l.slides){
    const text=JSON.stringify(s);
    assert.ok(!/лабораторн|ЛР\s?№/i.test(text),'Ссылка на лабораторную: '+s.id);
    assert.ok(pack.notes[s.id]?.script.trim(),'Нет сценария: '+s.id);
  }
  const task=l.slides.find(s=>s.practice);assert.ok(task);
  assert.equal(explanations[task.practice.solutionId],pack.notes[task.id].answer);
}
console.log(JSON.stringify({lectures:course.lectures.length,slides:course.lectures.reduce((n,l)=>n+l.slides.length,0),notes:Object.keys(pack.notes).length}));
