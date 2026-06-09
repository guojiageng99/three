"use client";

const roleMap: Record<string, string> = {
  Researcher: "研究者",
  Journalist: "记者",
  Florist: "花店店主",
};

const locationNameMap: Record<string, string> = {
  "Alice's Home": "Alice 家",
  "Johnson Park": "约翰逊公园",
  "Hobbs Cafe": "霍布斯咖啡馆",
  "Town Square": "镇中心广场",
};

const exactTextMap: Record<string, string> = {
  "A warm apartment with party notes on the table.": "桌上放着聚会笔记的温馨公寓。",
  "A calm open park for walking and chance encounters.": "适合散步和偶遇的安静公园。",
  "A small cafe where agents work and chat.": "角色会工作、聊天和相遇的小咖啡馆。",
  "The social center of the town.": "小镇最容易发生社交互动的中心区域。",
  "Preparing notes for tonight's gathering": "为今晚的聚会整理笔记",
  "Working at the cafe and inviting a friend": "在咖啡馆工作，并顺便邀请朋友",
  "Buying small decorations": "购买一些聚会装饰品",
  "Getting ready to host the gathering": "为晚上的聚会做最后准备",
  "Taking a morning walk": "晨间散步",
  "Writing in the cafe": "在咖啡馆写东西",
  "Meeting people in the square": "在广场与人交流",
  "Taking an evening walk": "傍晚散步",
  "Opening the flower stall": "整理并打开花摊",
  "Delivering flowers near the park": "去公园附近送花",
  "Selling flowers and chatting with neighbors": "卖花并和邻居聊天",
  "Closing the stall and checking town news": "收摊并留意镇上的消息",
  "Sharing a socially relevant update": "把一条重要社交信息告诉别人",
  "Reacting to new social information": "正在消化刚刚听到的新消息",
  "Reflecting on how the gathering has become shared town knowledge": "反思这场聚会如何变成全镇共享的信息",
  "Simulation ready": "模拟已就绪",
  "Party invitation shared": "聚会信息完成一次传播",
  "Reflection formed": "高层反思已经形成",
  "Casual social exchange": "普通社交对话",
  "The town wakes up. Alice has an evening gathering in mind, but only she knows about it yet.": "小镇开始运转。Alice 心里记着今晚的聚会，但目前只有她知道这件事。",
  "The agents now treat Alice's gathering as a shared town event rather than isolated information.": "此时，角色们已经把 Alice 的聚会看成全镇共享的事件，而不是某个人私下知道的小消息。",
  "Alice is hosting a small gathering tonight. You should stop by if you're free.": "Alice 今晚会办一个小聚会，你要是有空可以来看看。",
  "That sounds nice. I didn't know about it, but now I'm curious.": "听起来不错，我之前还不知道，现在有点想去了。",
  "The town feels especially connected today.": "今天镇上的人好像格外容易碰到彼此。",
  "It does. The same places keep bringing people together.": "确实，几个固定地点一直在把大家聚到一起。",
  "Tonight's gathering is starting to shape the day.": "今晚的聚会已经开始影响我今天的行动安排。",
  "Alice's gathering is turning into a shared town event, and I should factor it into later social choices.": "Alice 的聚会正在变成全镇共享的事件，我后续的社交决策要把这件事考虑进去。",
  "Recent encounters suggest the town's social rhythm is driven by repeated meetings at the same few places.": "最近的相遇说明，小镇的社交节奏主要由几个固定地点的重复碰面驱动。",
  "Alice knows the gathering and sees Bob nearby, so the social information is shared.": "Alice 知道聚会信息，而且看到了附近的 Bob，于是把这条社交信息告诉了他。",
  "Bob received new social information from Alice during the encounter.": "Bob 在这次相遇中从 Alice 那里得到了新的社交信息。",
  "Bob knows the gathering and sees Carol nearby, so the social information is shared.": "Bob 已经知道聚会信息，而且看到附近的 Carol，于是把消息继续传播了出去。",
  "Carol received new social information from Bob during the encounter.": "Carol 在这次相遇中从 Bob 那里得到了新的社交信息。",
  "A new high-level reflection was formed because the social information spread across the town.": "由于这条社交信息已经传播到全镇，系统因此生成了新的高层反思。",
  "I want tonight's gathering to feel casual and welcoming.": "我希望今晚的聚会轻松、自然，而且让人愿意参加。",
  "I should spend some time writing at the cafe today.": "我今天应该去咖啡馆待一会儿，顺便写点东西。",
  "The square is busiest in the afternoon.": "广场在下午通常最热闹。",
  "Alice is planning a small evening gathering and wants to invite a few friends naturally during the day.": "Alice 正在筹备今晚的小聚会，希望在白天自然地把几个朋友邀请过来。",
  "Bob likes learning what is happening around town and often passes news between people.": "Bob 很喜欢打听镇上发生了什么，也常常把消息在人与人之间传开。",
  "Carol notices community events quickly and often reacts by helping in practical ways.": "Carol 对社区里的事情很敏感，通常会用很实际的方式参与和帮忙。",
  "No strong memory cue.": "当前没有特别强的记忆线索。",
  "No nearby agents": "附近暂时没有其他角色",
  "Map View": "地图总览",
};

const eventTypeMap: Record<string, string> = {
  system: "系统",
  share: "传播",
  reflection: "反思",
  move: "移动",
  conversation: "对话",
};

const explanationTagMap: Record<string, string> = {
  "high importance": "重要性高",
  recent: "最近发生",
  "same location": "同一地点",
  "related to nearby agent": "与附近角色相关",
  "keyword overlap": "关键词重合",
  "baseline relevance": "基础相关",
  "explanation unavailable": "暂无解释",
};

const agentNameMap: Record<string, string> = {
  alice: "Alice",
  bob: "Bob",
  carol: "Carol",
};

function replaceExact(text: string): string {
  return exactTextMap[text] ?? text;
}

function translateStructuredText(text: string): string {
  let result = replaceExact(text.trim());

  result = result.replace(/^Heading to (.+)$/, (_match, location) => `前往${formatLocationName(location)}`);
  result = result.replace(
    /^I am at (.+), focused on (.+)\.$/,
    (_match, location, summary) => `我现在在${formatLocationName(location)}，正专注于${formatPlanSummary(summary)}。`,
  );
  result = result.replace(
    /^Following the plan at (.+) while thinking about tonight's gathering$/,
    (_match, location) => `按计划在${formatLocationName(location)}行动，同时一直想着今晚的聚会`,
  );
  result = result.replace(
    /^Following the plan at (.+) and mentally tracking tonight's gathering$/,
    (_match, location) => `按计划在${formatLocationName(location)}行动，并持续关注今晚聚会的安排`,
  );
  result = result.replace(
    /^I should mention tonight's gathering to (.+) if the moment feels natural\.$/,
    (_match, listener) => `如果时机合适，我应该把今晚聚会的事告诉 ${listener}。`,
  );
  result = result.replace(
    /^At (.+) around (\d{2}:\d{2}), (.+) tells (.+) about Alice's evening gathering\.$/,
    (_match, location, time, speaker, listener) => `${time} 左右，在${formatLocationName(location)}，${speaker} 把今晚聚会的消息告诉了 ${listener}。`,
  );
  result = result.replace(
    /^(.+) and (.+) exchange a few thoughts at (.+)\.$/,
    (_match, first, second, location) => `${first} 和 ${second} 在${formatLocationName(location)}简单聊了几句。`,
  );
  result = result.replace(
    /^I told (.+) about the gathering tonight\.$/,
    (_match, listener) => `我把今晚聚会的消息告诉了 ${listener}。`,
  );
  result = result.replace(
    /^(.+) told me about Alice's gathering tonight\.$/,
    (_match, speaker) => `${speaker} 告诉了我今晚聚会的消息。`,
  );
  result = result.replace(
    /^I had a short conversation with (.+) at (.+)\.$/,
    (_match, listener, location) => `我在${formatLocationName(location)}和 ${listener} 进行了一次简短对话。`,
  );
  result = result.replace(
    /^I moved to (.+) for (.+)\.$/,
    (_match, location, summary) => `我为了${formatPlanSummary(summary)}前往了${formatLocationName(location)}。`,
  );
  result = result.replace(
    /^(.+) moved$/,
    (_match, agentName) => `${agentName} 已移动`,
  );
  result = result.replace(
    /^(.+) left (.+) and went to (.+)\.$/,
    (_match, agentName, previous, next) => `${agentName} 离开了 ${formatLocationName(previous)}，前往 ${formatLocationName(next)}。`,
  );
  result = result.replace(
    /^Plan focus: (.+)\. Location: (.+)\. Nearby: (.+)\. Top memory cue: (.+)$/,
    (_match, summary, location, nearby, memoryCue) =>
      `当前计划重点：${formatPlanSummary(summary)}。当前位置：${formatLocationName(location)}。附近角色：${nearby === "No nearby agents" ? "暂无" : nearby}。最关键的记忆线索：${formatText(memoryCue)}`,
  );

  return replaceExact(result);
}

export function formatText(value: string | null | undefined): string {
  if (!value) {
    return "";
  }
  return translateStructuredText(value);
}

export function formatRole(role: string | null | undefined): string {
  if (!role) {
    return "未知角色";
  }
  return roleMap[role] ?? role;
}

export function formatLocationName(value: string | null | undefined): string {
  if (!value) {
    return "未知地点";
  }
  return locationNameMap[value] ?? value;
}

export function formatLocationDescription(value: string | null | undefined): string {
  return value ? formatText(value) : "";
}

export function formatPlanSummary(value: string | null | undefined): string {
  return value ? formatText(value) : "暂无计划";
}

export function formatActionText(value: string | null | undefined): string {
  return value ? formatText(value) : "当前暂无动作";
}

export function formatEventTitle(value: string | null | undefined): string {
  return value ? formatText(value) : "未命名事件";
}

export function formatEventDetail(value: string | null | undefined): string {
  return value ? formatText(value) : "暂无事件说明。";
}

export function formatEventTypeLabel(value: string | null | undefined): string {
  if (!value) {
    return "事件";
  }
  return eventTypeMap[value] ?? value;
}

export function formatKnowledgeBadge(knowsParty: boolean): string {
  return knowsParty ? "已知道聚会信息" : "暂不知道聚会信息";
}

export function formatModelMode(llmEnabled: boolean, llmModel: string | null): string {
  return llmEnabled ? llmModel ?? "LLM 模式" : "规则回退模式";
}

export function formatExplanationTag(tag: string): string {
  return explanationTagMap[tag] ?? tag;
}

export function formatAgentId(agentId: string): string {
  return agentNameMap[agentId.toLowerCase()] ?? agentId;
}
