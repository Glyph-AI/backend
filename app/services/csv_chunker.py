import csv


class CsvChunker:
    def chunk(self, content, chunk_size=1500):
        lines = content.splitlines()
        reader = csv.reader(lines)
        print("-" * 80)
        headers = next(reader)
        headers = ','.join(headers)
        chunks = []
        chunk_len = len(headers)
        current_chunk = [headers]
        for row in reader:
            # join row into string
            joined = ','.join(row)
            row_len = len(joined)
            chunk_len += row_len
            current_chunk.append(joined)
            # print(joined)

            if chunk_len > chunk_size:
                print(chunk_len)
                chunks.append('\n'.join(current_chunk))
                chunk_len = len(headers)
                current_chunk = [headers]

        return chunks
