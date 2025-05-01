-- retrospectives 테이블 생성
create table if not exists retrospectives (
    id bigint primary key generated always as identity,
    user_id text not null,
    good_points text not null,
    improvements text not null,
    learnings text not null,
    action_plan text not null,
    emotion_score integer not null check (emotion_score between 1 and 10),
    emotion_reason text not null,
    submitted_at timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
); 