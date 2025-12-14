// pages/api/chat.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { qdrant } from "../../src/lib/qdrant";
import { embeddingModel, gemini } from "../../src/lib/gemini";

type ResponseData = {
  answer: string;
  conversation_id: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method !== "POST") {
    return res.status(405).json({ answer: "POST only", conversation_id: "error" });
  }

  try {
    const { question = "", selected_text = "", conversation_id = "" } = req.body;

    if (!question.trim()) {
      return res.status(400).json({ answer: "Sawal likho bhai", conversation_id: "empty" });
    }

    const textToEmbed = selected_text ? `${selected_text}\n\n${question}` : question;
    const embedResult = await embeddingModel.embedContent(textToEmbed);
    const embedding = embedResult.embedding.values;

    // YE LINE UNIVERSAL HAI – SAB VERSION MEIN KAAM KAREGI
    const searchResult = await qdrant.search(
      process.env.QDRANT_COLLECTION || "hackathon-book",
      {
        vector: embedding,
        limit: 10,
        with_payload: true,
      }
    );

    const context = searchResult
      .map((hit: any) => hit.payload?.text || "")
      .filter(Boolean)
      .join("\n\n");

    const prompt = `Tu Physical AI & Humanoid Robotics book ka assistant hai.
Roman Urdu + English mein jawab de.

Context:
${context}

${selected_text ? `Selected text:\n${selected_text}\n` : ""}

Question: ${question}

Short aur clear jawab de.`;

    const result = await gemini.generateContent(prompt);
    const answer = result.response.text();

    res.status(200).json({
      answer: answer.trim(),
      conversation_id: conversation_id || `chat-${Date.now()}`,
    });

  } catch (error: any) {
    console.error("Chat API Error:", error);
    res.status(500).json({
      answer: "Server error ho gaya, refresh karo",
      conversation_id: "error",
    });
  }
}

export const config = { api: { bodyParser: true } };