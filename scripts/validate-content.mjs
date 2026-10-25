import fs from 'node:fs';
import assert from 'node:assert/strict';
import {validateCourse} from '../src/engine/model.ts';
import {validateTeacherPack,validateBank,courseAssets} from '../src/engine/validation.ts';
const course=JSON.parse(fs.readFileSync('public/course.json','utf8'));
const pack=JSON.parse(fs.readFileSync('public/teacher-pack.json','utf8'));
const explanations=JSON.parse(fs.readFileSync('public/explanations.json','utf8'));
validateCourse(course);validateTeacherPack(pack,course);
const bank=JSON.parse(fs.readFileSync('public/assessment.json','utf8'));
const models=JSON.parse(fs.readFileSync('public/workbenches.json','utf8'));
const coverage=JSON.parse(fs.readFileSync('authoring/detailed-coverage.json','utf8'));
validateBank(bank,course);
assert.deepEqual(coverage.missingLectures,[]);
assert.equal(course.lectures.length,31);
for(const [semester,count] of [[5,19],[6,7],[7,5]])assert.equal(course.lectures.filter(l=>l.semester===semester).length,count);
for(const asset of courseAssets(course))if(!/^https?:/.test(asset))assert.ok(fs.existsSync('public/'+asset),asset);
for(const l of course.lectures){
  assert.equal(l.slides[0].kind,'title');
  assert.deepEqual(l.slides.slice(0,5).map(s=>s.kind),['title','literature','literature','materials','agenda']);
  assert.equal(l.slides.filter(s=>s.kind==='section').length,4,l.id);
  assert.equal(l.slides.filter(s=>s.id.includes('-definition-')).length,8,l.id);
  assert.equal(l.slides.filter(s=>s.task).length,16,l.id);
  assert.equal(l.slides.filter(s=>s.learning?.passport).length,4,l.id);
  for(const s of l.slides){
    const text=JSON.stringify(s);
    assert.ok(!/лабораторн|ЛР\s?№/i.test(text),'Ссылка на лабораторную: '+s.id);
    assert.ok(pack.notes[s.id]?.script.trim(),'Нет сценария: '+s.id);
    if(s.learning){
      const model=models[s.learning.id];assert.ok(model,s.id);
      assert.equal(model.scenarios.length,2);
      for(const scenario of model.scenarios){
        assert.ok(scenario.frames.length>=4,s.id);
        assert.ok(scenario.accepted.length>0,s.id);
      }
    }
    if(s.task?.options)assert.equal(new Set(s.task.options.map(o=>o.text)).size,s.task.options.length,s.id);
  }
  for(const task of l.slides.filter(s=>s.practice))assert.equal(explanations[task.practice.solutionId],pack.notes[task.id].answer);
  assert.ok(l.slides.find(s=>s.id===l.id+'-integrated-practice'));
}
console.log(JSON.stringify({lectures:course.lectures.length,slides:course.lectures.reduce((n,l)=>n+l.slides.length,0),notes:Object.keys(pack.notes).length}));
