// pages/api/rag.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { qdrant } from "../../src/lib/qdrant";
import { embeddingModel, gemini } from "../../src/lib/gemini";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Only POST allowed" });
  }

  try {
    const { message = "", history = [], pageContent = "" } = req.body;

    if (!message.trim()) {
      return res.status(400).json({ error: "Message bhejo bhai" });
    }

    const embedResult = await embeddingModel.embedContent(message);
    const userEmbedding = embedResult.embedding.values;

    // YE LINE BHI PURANE AUR NAYE DONO VERSION MEIN 100% CHALEGI
    const searchResult = await qdrant.search(
      process.env.QDRANT_COLLECTION || "hackathon-book",
      {
        vector: userEmbedding,
        limit: 8,
        with_payload: true,
      }
    );

    const context = searchResult
      .map((r: any) => r.payload?.text || "")
      .filter(Boolean)
      .join("\n\n");

    const fullPrompt = `Tu Physical AI & Humanoid Robotics ka expert hai.
Roman Urdu + English mein jawab de.

Context:
${context}

${pageContent ? `Current page:\n${pageContent.slice(0, 8000)}` : ""}

Sawal: ${message}

Sirf context se jawab de, bilkul clear aur short.`;

    const result = await gemini.generateContent(fullPrompt);
    const reply = result.response.text();

    res.status(200).json({ reply: reply.trim() });

  } catch (error: any) {
    console.error("RAG API Error:", error);
    res.status(500).json({ error: "Server error: " + error.message });
  }
}

export const config = {
  api: {
    bodyParser: true,
  },
};