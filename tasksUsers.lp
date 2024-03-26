time(1..32).
days(1..7).


1 { assignment(C,U,D,T,DA) : user(U,ID),time(T),days(DA)}  :- task(C,D).

%Need to represent the idea of the total time of the tasks assigned to the user does not exceed a certain amount


%A constraint is defined to make sure that the same task is not assigned to the same
:- assignment(C1, _,_,_,_), assignment(C2,_,_,_,_), C1 != C2.

assignment(_,_,_,T,_):-time(T)!=T+1.

:-user(U), #sum {assignment(_,U,_,_,DA): days(DA)}<=2





%NUMBER

% Defines a task and its relevant taskID in the 
% JSON file, also acts as a way of retriving only the
%taskID of a certain task
% time(1..4).
% 1{assignment(D,U,C,T): date(D), user(U), chore(C), time(T)} 1:-chore(C).
% %This accounts for the conflict between two chores being assigned at the same time 
% :- assignment(D,U,C1,T1), assignment(D,U,C2,T2), C1!=C2, T1!=T2.

% avaliableUser(U) :- assignment(_,U,_,_).
% #minimize{1@2,U :avaliableUser(U)}.
% #minimize{T@1,U: assignment(D,U,C,T)}.